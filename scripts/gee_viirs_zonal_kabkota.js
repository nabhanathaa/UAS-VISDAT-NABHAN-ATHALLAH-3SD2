/******************************************************************************
 * UAS Visualisasi Data dan Informasi 2026 — "Terang, Kaya, Sejahtera?"
 * Nabhan Athallah (3SD2 / 222313272)
 *
 * SKRIP GOOGLE EARTH ENGINE (Code Editor, JavaScript)
 * Tujuan : statistik zonal cahaya malam VIIRS untuk 514 kabupaten/kota
 * Output : 1 tabel CSV: 514 kab/kota x 2 tahun (2020 dan 2024)
 *          - 2024 = tahun utama (sama dengan seluruh data BPS)
 *          - 2020 = pembanding untuk (a) pertumbuhan cahaya 2020–2024 dan
 *                   (b) topik migrasi (data migrasi BPS mengacu ke 2020)
 *
 * ----------------------------------------------------------------------------
 * 1. SPESIFIKASI DATA SATELIT
 * ----------------------------------------------------------------------------
 * Dataset      : 2020 → NOAA/VIIRS/DNB/ANNUAL_V21 (V2.1; katalog GEE 2012–2020)
 *                2024 → NOAA/VIIRS/DNB/ANNUAL_V22 (V2.2; dipakai untuk 2022+)
 *                Produsen dan metode sama (EOG), nama band sama; perbedaan
 *                versi dicatat sebagai keterbatasan di makalah.
 *                "VIIRS Nighttime Day/Night Annual Band Composites"
 *                Earth Observation Group (EOG), Payne Institute, Colorado
 *                School of Mines — Elvidge et al. (2021), Remote Sensing 13(5):922
 *                Katalog: developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_ANNUAL_V22
 * Sensor       : VIIRS Day/Night Band (DNB) pada satelit Suomi NPP (NASA/NOAA)
 * Resolusi     : 15 arc-second ≈ 463,83 m (di ekuator)
 * Temporal     : komposit TAHUNAN (1 citra per tahun), tersedia 2012–2024;
 *                yang dipakai hanya 2020 dan 2024
 * Satuan       : nW/cm²/sr (nanowatt per sentimeter persegi per steradian)
 * Band dipakai :
 *   - average_masked : rata-rata radiance tahunan SETELAH penyaringan:
 *                      piksel berawan dibuang (cloud mask VIIRS),
 *                      cahaya bulan & stray light dikoreksi,
 *                      cahaya sementara/ephemeral (kebakaran, kapal, dsb.)
 *                      dan latar belakang (non-lit) di-mask.
 *                      → band utama untuk analisis.
 *   - cf_cvg         : jumlah observasi BEBAS AWAN dalam setahun (quality flag).
 *                      Nilai rendah = estimasi kurang andal (daerah sering berawan).
 * Catatan awan : kualitas komposit tahunan bergantung pada jumlah malam bebas
 *                awan; karena itu cf_cvg ikut diekspor sebagai indikator mutu.
 * Keterbatasan : saturasi di pusat kota besar kecil kemungkinannya (DNB tidak
 *                mudah jenuh), tetapi gas flare/industri migas dapat tetap
 *                terekam; daerah sering berawan (Papua pegunungan) bisa bias.
 *
 * ----------------------------------------------------------------------------
 * 2. METODE STATISTIK ZONAL
 * ----------------------------------------------------------------------------
 * - Poligon  : asset kabkota_514_gee (geoBoundaries IDN ADM2, BPS–WFP–OCHA,
 *              514 kab/kota, kolom kunci 'kode_bps').
 * - Piksel yang di-mask (latar belakang) diisi 0 (unmask) agar luas wilayah
 *   tetap dihitung penuh dan rata-rata tidak bias ke atas.
 * - reduceRegions pada skala asli 463,83 m; piksel di tepi poligon diberi
 *   bobot sesuai porsi luas yang tercakup (perilaku default EE untuk sum/mean).
 * - Variabel yang dihasilkan per kab/kota per tahun:
 *     rad_sum   = Σ radiance (Sum of Lights, SOL)            → cahaya per kapita
 *     rad_mean  = rata-rata radiance per piksel               → intensitas per area
 *     rad_max   = radiance maksimum (pusat kota)              → cek pencilan
 *     lit_share = proporsi piksel menyala (> AMBANG)          → % luas menyala
 *     n_pix     = jumlah piksel (berbobot) dalam poligon      → kontrol luas
 *     cfcvg_mean= rata-rata observasi bebas awan              → mutu data
 * - AMBANG piksel menyala = 0,5 nW/cm²/sr (uji sensitivitas 0,3 dan 1,0 bisa
 *   dilakukan dengan mengganti nilai AMBANG lalu menjalankan ulang).
 *
 * ----------------------------------------------------------------------------
 * 3. CARA PAKAI
 * ----------------------------------------------------------------------------
 *  a) Assets → NEW → Shape files → pilih kabkota_514_untuk_GEE.zip
 *     → nama asset: kabkota_514_gee → tunggu Tasks selesai.
 *  b) Ganti ASSET_ID di bawah dengan path asset Anda.
 *  c) Run → cek Console (jumlah fitur harus 514; baris hasil 1.028).
 *  d) Tab Tasks → RUN pada 'viirs_kabkota_2020_2024' → CSV tersimpan di
 *     Google Drive folder 'UAS_VISDAT'.
 *  e) Simpan CSV ke data_olah/01_tabular/ lalu gabungkan di notebook.
 ******************************************************************************/

// ============================ PARAMETER ====================================
var ASSET_ID  = 'projects/teknbigdata/assets/kabkota_514_gee';
var TAHUN     = [2020, 2024];   // daftar tahun (JavaScript biasa)
var AMBANG    = 0.5;            // nW/cm²/sr, batas piksel "menyala"
var SKALA     = 463.83;         // meter, resolusi asli VIIRS VNL
var FOLDER    = 'UAS_VISDAT';

// ============================ DATA ==========================================
var kab = ee.FeatureCollection(ASSET_ID);
var v21 = ee.ImageCollection('NOAA/VIIRS/DNB/ANNUAL_V21');   // 2012–2020
var v22 = ee.ImageCollection('NOAA/VIIRS/DNB/ANNUAL_V22');   // 2022 dst.

// Cek tahun yang tersedia di masing-masing koleksi
var tahunDari = function (ic) {
  return ic.aggregate_array('system:time_start').map(function (t) { return ee.Date(t).get('year'); });
};
print('Tahun tersedia V2.1:', tahunDari(v21));
print('Tahun tersedia V2.2:', tahunDari(v22));
print('Jumlah kab/kota (harus 514):', kab.size());

// Ambil satu citra tahunan (tahun = angka JavaScript biasa)
function ambilTahun(tahun) {
  var koleksi = (tahun <= 2021) ? v21 : v22;
  var versi   = (tahun <= 2021) ? 'V2.1' : 'V2.2';
  var ic = koleksi.filterDate(tahun + '-01-01', (tahun + 1) + '-01-01');
  print('Citra ' + tahun + ' (' + versi + ') jumlah (harus 1):', ic.size());
  return {img: ee.Image(ic.first()), versi: versi};
}

// ============================ FUNGSI ZONAL ==================================
var reducer = ee.Reducer.sum().setOutputs(['sum'])
  .combine({reducer2: ee.Reducer.mean().setOutputs(['mean']),   sharedInputs: true})
  .combine({reducer2: ee.Reducer.max().setOutputs(['max']),     sharedInputs: true})
  .combine({reducer2: ee.Reducer.count().setOutputs(['count']), sharedInputs: true});

function zonalTahun(tahun) {
  var x   = ambilTahun(tahun);
  var rad = x.img.select('average_masked').unmask(0).rename('rad');
  var lit = rad.gt(AMBANG).rename('lit');
  var cf  = x.img.select('cf_cvg').unmask(0).rename('cf');

  // 1) radiance: total (sum), rata-rata, maksimum, jumlah piksel
  var r1 = rad.reduceRegions({collection: kab, reducer: reducer, scale: SKALA, tileScale: 4});
  // 2) proporsi piksel menyala & rata-rata malam bebas awan
  var r2 = lit.addBands(cf).reduceRegions({collection: kab, reducer: ee.Reducer.mean(), scale: SKALA, tileScale: 4});

  // gabungkan r1 & r2 berdasarkan kode_bps
  var join = ee.Join.inner().apply(r1, r2, ee.Filter.equals({leftField: 'kode_bps', rightField: 'kode_bps'}));
  return join.map(function (p) {
    var a = ee.Feature(p.get('primary')), b = ee.Feature(p.get('secondary'));
    return ee.Feature(null, {
      kode_bps:   a.get('kode_bps'),
      nama:       a.get('nama'),
      tahun:      tahun,
      versi_vnl:  x.versi,
      rad_sum:    a.get('sum'),
      rad_mean:   a.get('mean'),
      rad_max:    a.get('max'),
      n_pix:      a.get('count'),
      lit_share:  b.get('lit'),
      cfcvg_mean: b.get('cf')
    });
  });
}

var hasil = ee.FeatureCollection(TAHUN.map(zonalTahun)).flatten();
print('Jumlah baris hasil (harus 1028 = 514 x 2):', hasil.size());
print('Contoh 5 baris 2024:', hasil.filter(ee.Filter.eq('tahun', 2024)).limit(5));

// ============================ CEK VISUAL ===================================
var v24 = ambilTahun(2024).img;
Map.setCenter(118, -2.5, 5);
Map.addLayer(v24.select('average_masked'), {min: 0, max: 30,
  palette: ['000004', '3b0f70', '8c2981', 'de4968', 'fe9f6d', 'fcfdbf']}, 'VIIRS 2024 (nW/cm²/sr)');
Map.addLayer(v24.select('cf_cvg'), {min: 0, max: 60,
  palette: ['d55e00', 'f0e442', '009e73']}, 'Malam bebas awan 2024', false);
Map.addLayer(kab.style({color: '56B4E9', fillColor: '00000000', width: 0.6}), {}, 'Batas 514 kab/kota');

// ============================ EKSPOR =======================================
Export.table.toDrive({
  collection:  hasil,
  description: 'viirs_kabkota_2020_2024',
  folder:      FOLDER,
  fileFormat:  'CSV',
  selectors:   ['kode_bps', 'nama', 'tahun', 'versi_vnl', 'rad_sum', 'rad_mean', 'rad_max',
                'n_pix', 'lit_share', 'cfcvg_mean']
});
