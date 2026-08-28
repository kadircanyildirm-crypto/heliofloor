# Surya'nın Güneş Patlaması Tahmininin Bağımsız Değerlendirmesi

### Ucuz taban çizgileri, 366 milyon parametreli temel modelle başa baş gidiyor

**Kadir Can Yıldırım**  
Bağımsız araştırmacı, Eskişehir, Türkiye  
kadir.can.yildirm@gmail.com · ORCID: [0009-0008-5098-2547](https://orcid.org/0009-0008-5098-2547)

**Taslak sürüm 0.6**

**Anahtar kelimeler:** güneş patlaması tahmini, temel modeller, kıyaslama
değerlendirmesi, model kalibrasyonu, uzay havası, taban çizgisi karşılaştırması,
taban-oran kayması

*(İngilizce başlık: "An Independent Evaluation of Surya's Solar Flare
Forecasting: Cheap Baselines Match a 366M-Parameter Foundation Model")*

> Bu metin `PAPER_DRAFT.md`'nin Türkçe çevirisidir; yayımlanan sürüm
> İngilizcedir. Sayılar, iddialar ve bölüm numaraları birebir aynıdır.
> Teknik terimlerin İngilizcesi ilk geçtiği yerde parantez içinde, alıntılar
> önce İngilizce aslıyla verilmiştir.

Aşağıdaki her sayı `verify_paper.py` ile ham veriden yeniden hesaplanıyor:
**161 iddianın 161'i geçiyor** — önyükleme aralıklarının birebir yeniden
üretimi dahil.

---

## Özet

Surya, NASA ve IBM'in yayımladığı 366 milyon parametreli bir helyofizik temel
modeli. Solar Dynamics Observatory (SDO) görüntüleriyle eğitilmiş. Makalesi, iki
derin öğrenme görüntü modeline karşı **TSS 0.436** (HSS 0.522, F1 0.561) değerinde
bir patlama tahmini sonucu bildiriyor.

Biz bu modelin yayımlanan `solar_flares_surya` kontrol noktasını bildiğimiz kadarıyla ilk kez bağımsız
olarak değerlendirdik. Ham SDO girdilerini resmî arşivden akıtarak modeli
**2011–2024 arasından 1.146 tahmin saatinde** puanladık; bunların 218'i pozitif.
Ayrıca GPU gerektirmeyen ucuz taban çizgilerini eksiksiz resmî bölümlerde
çalıştırdık: 3.672 doğrulama ve 43.848 test saati.

Beş bulgumuz var. Bunları en sağlam destekleneninden başlayarak sıralıyoruz.

**(i) Kıyaslamanın etkin örneklemi göründüğünden çok küçük.** Aynı 24 saatlik blok
içindeki tahmin saatleri birbirine sıkı sıkıya bağlı. Yani kanıt birimi saat değil,
blok. 739 doğrulama saatimiz 50 bloğa yayılıyor ve bu blokların **yalnızca 6'sında
pozitif var**. 407 test saati 28 bloğa yayılıyor, 11'inde pozitif var. Blok
önyüklemesi (block bootstrap) buna göre 0.46–0.81 TSS genişliğinde aralıklar
veriyor. Eşleştirilmiş farklar on yöntem çiftinin sekizinde sıfırı kapsıyor.
En güçlü ayrışma şu: sevk edilen 0.5 eşiği, test penceresinde 24 saatlik
kalıcılığın anlamlı şekilde altında kalıyor (ΔTSS −0.445, %95 GA
[−0.825, −0.086]). On yönlü aile düzeltmesinden ise hiçbir çift sağ çıkmıyor;
bu da yetersiz güç tezinin kendisi.

**(ii) Kalibrasyon rejime bağlı ve aktarılamıyor.** Surya'nın olasılıkları
doğrulama penceresinde gerçeğe yakın: Brier 0.057. Test penceresinde çöküyor: Brier
0.208. Somut örnek: 15 bağımsız blok boyunca, modelin 0.05–0.25 arası olasılık
verdiği saatlerin **%56.6'sını** bir patlama izliyor. Modelin o saatler için
ortalama öngörüsü ise 0.148. Doğrulama verisinde uydurulan bir Platt düzeltmesi
neredeyse hiçbir şeyi değiştirmeyen bir eşleme çıkarıyor.

**(iii) Ucuz ve görüntüsüz bir model, temel modelle başa baş gidiyor ya da onu
geçiyor.** Son bir
haftanın GOES X-ışını akısına bakan 11 özellikli bir lojistik regresyon kurduk. Bir
CPU'da saniyeler içinde eğitiliyor. Aynı doğrulama saatlerinde Surya ile başa baş
(0.685'e karşı 0.673), aynı test saatlerinde onu geçiyor (0.738'e karşı 0.632); bu fark eşleştirilmiş
önyüklemede sıfırı kıl payı da olsa dışlıyor. Eksiksiz bölümlerde 0.661 ve 0.554 alıyor; ikisi de bildirilen 0.436'nın üstünde.
Bu son karşılaştırmayı bildiriyoruz ama eşleştirilmemiş olarak işaretliyoruz.

**(iv) Hiçbir sıradan taban çizgisi bildirilmemiş.** 24 saatlik kalıcılık kuralı
(persistence) tek başına tam doğrulama bölümünde 0.430 alıyor. Bu değerin %95
aralığı **[0.238, 0.621]** ve bildirilen 0.436'yı içine alıyor.

**(v) Beceri rejime göre bölünmüş görünüyor, ama sadece yapısal yarısı ölçülebilir.**
Kalıcılık kuralı bir patlama epizodunun başlangıcını yapısı gereği göremez; sönme
sürecinin de her saatinde yanlış alarm verir. Modelin başlangıçlardaki davranışı
ise sadece **4 ve 3 bağımsız bloğa** dayanıyor. Bu kadar veri betimlemeye yeter,
tahmine yetmez. O yüzden bunu bir oran olarak değil, bir gözlem olarak bildiriyoruz.

**(ii) ve (v) bulgularının ortak nedeni var:** taban oranının durağan olmaması.
Resmî test bölümünde pozitif oranı 2020'de 0.0055 iken 2024'te 0.697'ye çıkıyor.
Güneş döngüsü boyunca **128 katlık** bir kayma. Eşik sabit tutulduğunda iki ucuz yöntem
zıt yönlere gidiyor; yine de havuzlanmış test TSS'i ikisinde de her yıllık
değerin üstünde çıkıyor: klasik Simpson paradoksu. (i)'in nedeni ayrı, saatlerin
birbirine bağlı olması ve olayların seyrekliği. (iii)'ün nedeni de ayrı,
X-ışını kaydının zaten taşıdığı bilgi.

Ölçümlerimizden bağımsız olarak şunu da belgeliyoruz: **bildirilen 0.436'nın hangi
döneme ait olduğu bulunamıyor.** Yayımlanan kaynaklar birbirini tutmayan üç bölüm
tanımı veriyor ve sonuç tablosu bunların hiçbirini söylemiyor. Üstelik iki kardeş
makale, aynı görevde aynı model için ResNet50'yi bir yerde TSS 0.018, öbür yerde
0.261 olarak bildiriyor. Yani referans seviyesi, iddia edilen farktan daha oynak.

Bu yüzden sorunun Surya'ya özgü olmadığını savunuyoruz. Sorun **değerlendirme
protokolünün kendisinde.** Somut düzeltmeler öneriyoruz: ucuz taban çizgileri
zorunlu olsun, havuzlanmış yerine rejim bazlı raporlama yapılsın, eşik prosedürü
açıkça yazılsın, belirsizlik aralıkları zamansal bloklar üzerinden hesaplansın.

---

## 1. Giriş

Temel modeller (foundation models) fizik bilimlerine girmeye başladı. Helyofizik
bu gelişin en yeni duraklarından biri. Surya, Ağustos 2025'te NASA ve IBM
tarafından yayımlandı (Roy ve ark. 2025). 366 milyon parametreli bir dönüştürücü,
SDO görüntüleriyle eğitilmiş ve birkaç aşağı akış görevi için uyarlanmış
başlıklarla açık şekilde paylaşılmış. Yayımla birlikte SuryaBench adlı kıyaslama
takımı da geldi (Roy ve ark. 2026). Bu takımın patlama tahmini görevi basit
görünen bir soru soruyor: *t* anındaki tam disk güneş görüntülerine bakarak,
önümüzdeki 24 saatte GOES yumuşak X-ışını akısı M1.0'ı aşacak mı?

Bu tür kıyaslamalar sadece model ölçmez. Alanın neyi ilerleme sayacağını da
belirler. Bildirilen bir skor, sonraki çalışmaların geçmeye çalıştığı sayı olur.
Fon başvurularında atıf verilen sayı olur. Operasyonel kullanıcıların "bu iş artık
hazır mı" diye bakarken gördüğü sayı olur. Dolayısıyla değerlendirmenin tasarımı
en az modelin kendisi kadar etkilidir. Hangi taban çizgileri var, skor nasıl
toplanıyor, belirsizlik veriliyor mu — bunların hepsi tasarım kararı.

Buna rağmen bu modellerin bağımsız değerlendirmesi nadir yapılır. Sebep sıradan:
pahalı. Bu görevdeki her tahmin saati, 4096² çözünürlükte 13 kanallı iki SDO zaman
adımı istiyor. Mütevazı bir örneklemi puanlamak bile bir GPU üzerinden yüzlerce
gigabayt akıtmak demek. Sonuç şu: bildirilen sayılar sorgulanmadan kalıyor.
Sorgulanamaz oldukları için değil, sorgulamanın maliyeti çoğu grubun bütçesini
aştığı için.

Bu makale, o bedeli ödediğimizde ne bulduğumuzu anlatıyor. Yayımlanan kontrol
noktasını yazarların kendi çıkarım koduyla çalıştırdık ve 2011–2024 arasından 1.146
tahmin saatinde değerlendirdik. Ucuz taban çizgileri hiç GPU istemediği için,
onları eksiksiz resmî bölümlerde çalıştırdık: 3.672 doğrulama ve 43.848 test saati. Bildiğimiz kadarıyla bu kontrol noktasının yayımlanmış başka bir
bağımsız değerlendirmesi yok.

Altı katkımız var. İlk beşi ölçüm ve birbirini besliyor. Altıncısı belgesel
nitelikte, hiçbir deneye bağlı değil.

**1. Kıyaslama hiçbir ucuz taban çizgisi bildirmiyor.** Karşılaştırdığı tek şey iki
görüntü modeli: AlexNet ve ResNet50. Oysa hiçbir model gerektirmeyen 24 saatlik
kalıcılık kuralı, tam doğrulama bölümünde zaten TSS 0.430 alıyor. Bu değerin gün
bloklu %95 aralığı **[0.238, 0.621]** ve temel model için bildirilen 0.436'yı içine
alıyor.

**2. Ucuz ve görüntüsüz bir model temel modelle başa baş gidiyor, hatta geçiyor.**
*Aynı* tahmin saatlerinde ölçtük. 11 özellikli lojistik regresyon doğrulamada Surya
ile eşit (0.685'e karşı 0.673), testte onu geçiyor (0.738'e karşı 0.632). Eksiksiz
bölümlerde 0.661 ve 0.554 alıyor, bildirilen 0.436'nın üstünde. Bu son
karşılaştırmayı eşleştirilmemiş olarak işaretliyoruz, çünkü modelin tam bölüm
çıkarımı bütçemizi aşıyordu.

**3. Bu görevde tek sayılı karşılaştırmalar yetersiz güçte.** Aynı bloktaki tahmin
saatleri birbirine bağlı. Blokları bütün olarak yeniden örneklediğimizde %95
aralıkları 0.46–0.81 TSS genişliğinde çıkıyor. Eşleştirilmiş farklar on çiftin
sekizinde sıfırı kapsıyor; en güçlü ayrışma bile — sevk edilen eşiğin testte
kalıcılığın altında kalması — on yönlü aile düzeltmesinden sağ çıkmıyor.

**4. Beceri rejime bölünmüş görünüyor ve iki rejim birbirini tamamlıyor.**
Kalıcılık kuralı epizot başlangıçlarına kördür ve her sönme saatinde yanlış alarm
verir. Bu tanımsal bir gerçek, örneklem büyüklüğünden bağımsız. Modelin
başlangıçlardaki tamamlayıcı davranışını örneklemimizde görüyoruz. Ama §4.4'te
göstereceğimiz gibi, bunu bir oran olarak söyleyemeyecek kadar az epizot var.

**5. Kalibrasyon rejime bağlı ve aktarılamıyor.** Surya'nın olasılıkları doğrulama
penceresinde gerçeğe yakın, test penceresinde çöküyor. Doğrulamada uydurulan
düzeltme test penceresine neredeyse hiçbir şey yapmadan geçiyor.

**6. Bildirilen skorun hangi döneme ait olduğu bulunamıyor.** Ortada birbirini
tutmayan üç bölüm tanımı var ve sonuç tablosu hiçbirini söylemiyor. İki kardeş
makale aynı taban çizgisi için on dört kat farklı TSS veriyor. Veri belgeleri, kendi
etiketlerinin izlediğinden on kat uzak bir olay eşiği yazıyor. Bu bir ölçüm değil,
kamuya açık kaydın okunması. Kaynaklarıyla §2.3'te.

4. ve 5. katkılar ile §4.6'daki eşik davranışı aynı nedene dayanıyor. Resmî test
bölümünde pozitif oranı, güneş döngüsü maksimuma tırmanırken 0.0055'ten 0.697'ye
çıkıyor. Tek bir bölüm içinde 128 katlık kayma. Eşik sabitken ucuz yöntemler zıt yönlere
gidiyor. Bölümü havuzlamak ise ikisi için de hiçbir tekil yılda görülmeyen kadar
yüksek bir skor üretiyor. 3. katkının nedeni farklı: saatlerin birbirine bağlı
olması ve olayların seyrekliği. 2. katkının nedeni de farklı: 24 saatlik patlama
sinyalinin ne kadarını X-ışını kaydının zaten taşıdığı.

Bu yüzden çalışmamızı bir modelin değil, bir değerlendirme protokolünün
eleştirisi olarak sunuyoruz. Yazarların kendisi zaten şunu yazmış:

> *"It should also be noted that these models serve as proof-of-concept studies
> and are not optimized for end-to-end or operational forecasting use."*
>
> "Ayrıca belirtmek gerekir ki bu modeller kavram ispatı çalışmalarıdır ve uçtan
> uca veya operasyonel tahmin kullanımı için optimize edilmemiştir."

Bu çekinceyi olduğu gibi kabul ediyoruz. Bizim iddiamız daha dar: kavram ispatı düzeyinde bile bu protokol yöntemleri sıralayamıyor.
Çünkü görüntünün katkısı, X-ışını geçmişinin tek başına sağladığından hiçbir zaman
ayrıştırılmıyor. Bu yeteneği geri kazandıracak altı somut değişiklikle bitiriyoruz.
Hepsi ucuz.

## 2. Arka plan

### 2.1 Surya ve SuryaBench

Surya 13 SDO kanalı üzerinde çalışıyor: 8 AIA kanalı (yedi EUV ve 1600 Å'da bir UV)
ve 5 HMI kanalı (görüş doğrultusunda manyetik alan, üç vektör bileşeni, Doppler
hızı). Doğal çözünürlük 4096². Hugging Face'te Apache 2.0 lisansıyla, LoRA ile
uyarlanmış aşağı akış başlıklarıyla yayımlandı.

Ön eğitim verisinin boyutu konusunda bilerek dikkatli konuşuyoruz, çünkü
**yayımlanan kaynaklar birbirini tutmuyor.** Model makalesi veri tabanının
*"May 13, 2010, to December 31, 2024"* aralığını kapsadığını ve toplam boyutunun
*"around 257 TB"* olduğunu söylüyor. Ön eğitim bölümlemesi için de *"observations
from 2011 to 2019"* diyor. Hugging Face model kartı ise modeli *"pretrained on 9
years (≈218 TB) of multi-instrument data"* diye tanıtıyor. **"218" ve "dokuz yıl"
ifadeleri makalede hiç geçmiyor.**

İkisinin birbiriyle nasıl ilişkilendiğini hiçbir kaynak söylemiyor: makale
218 TB'yi hiç anmıyor, model kartı 257 TB'yi hiç anmıyor, ve ikisi de dokuz
yıllık ön eğitim külliyatını 2010–2024 veri tabanına bağlamıyor. 218 TB'yi tek
kaynağı olan model kartına atfediyoruz; iki rakamı yazarların yerine
uzlaştırmıyoruz. Bu küçük örnek, §2.3'te
göstereceğimiz daha büyük bir örüntünün parçası.

### 2.2 Patlama tahmini görevi

Görev ikili (binary): GOES yumuşak X-ışını akısının zirvesi, [t, t+24s) penceresinde
θ_max = 10⁻⁵ W m⁻² eşiğini (M1.0) aşıyor mu? Çözünürlük saatlik. Model girdisi iki
zaman adımı: t−60 dakika ve t.

Resmî bölümler, yayımlanan CSV dosyalarında göründüğü hâliyle şöyle:

| bölüm | yıllar | takvim aralığı | saat | taban oranı |
|---|---|---|---|---|
| eğitim | 2010–2019 | 15 Şub – 31 Ara | 74.760 | 0.1211 |
| doğrulama | 2011–2019 | 15–31 Oca | 3.672 | 0.1089 |
| `leaky_validation` | 2011–2019 | 1–14 Oca ve 1–14 Şub | 6.048 | 0.1490 |
| test | 2020–2024 | tüm yıl | 43.848 | 0.2943 |

Bu sayıları doğrudan dosyalardan saydık. Veri kartı doğrulama ve
`leaky_validation` bölümlerini 2010–2019 diye tanıtıyor ama **2010 iki dosyada da
yok.** Hesap tutuyor: 3.672 = 17 gün × 24 saat × 9 yıl.

Bu tasarımın ileride önem kazanacak iki özelliği var. Birincisi, doğrulama bölümü
eğitimle aynı yıllardan alınmış Ocak pencerelerinden oluşuyor. Yazarlar komşu
bölüme `leaky_validation`, yani "sızıntılı doğrulama" adını vererek bunu zaten
kabul etmiş. İkincisi, test bölümü güneş döngüsü 25'in dik yükseliş evresini
kapsıyor. Yani taban oranı sabit değil. Bu §4.6'nın konusu.

### 2.3 Bildirilen sonuçlar ve neden bulunamadıkları

Model makalesinin Tablo 4'ü Surya'yı TSS 0.436 / HSS 0.522 / F1 0.561 olarak
veriyor. Karşısında AlexNet (0.358 / 0.398 / 0.454) ve ResNet50 (0.018 / 0.028 /
0.055) var. İkisi de görüntü modeli.

**Değerlendirme bölümü yazılmamış. Karar eşiği prosedürü yazılmamış. Hiçbir
belirsizlik verilmemiş. Görüntü kullanmayan bir taban çizgisi yok.**

İlgili bölümü baştan sona okuduk. Önce etiketi tanımlıyor, sonra metrikleri, sonra
tabloyu sunuyor. Bu görev için ne bölümleme var, ne tarih aralığı, ne örneklem
sayısı. Bir olasılığın nasıl ikili tahmine çevrildiği de yazmıyor.

Durum basit bir eksiklikten kötü. Çünkü yayımlanan kaynaklar, eksik bölüm için
**birbirini tutmayan üç aday** sunuyor:

| kaynak | eğitim | doğrulama | test |
|---|---|---|---|
| model makalesi §2.1.2 (ön eğitim için) | 2011–2019, gün 46–365 | — | 2011–2019, gün 15–31 |
| SuryaBench makalesi (çekirdek SDO verisi için) | 2010–2018 | 2019 | 2020 |
| Hugging Face veri kartı | 2010–2019, 15 Şub – 31 Ara | 15–31 Oca | 2020–2024 |

Model makalesinin bölümlemesi SDO-veri kısmında veriliyor ve aşağı akış
görevleriyle hiç ilişkilendirilmiyor. SuryaBench'in rakamı çekirdek veri kümesine
ait; dosya sayıları (379.920 / 43.680 / 43.800) saatlik patlama göreviyle hiç
örtüşmüyor. Tablo 4 bunların hiçbirini adıyla anmadığı için, **TSS 0.436 belirli
bir değerlendirme dönemine atfedilemiyor.** Bizim tahminimiz 15–31 Ocak doğrulama
penceresi olduğu yönünde. Ama bu bir çıkarım ve önem taşıdığı her yerde öyle
işaretliyoruz.

İkinci tutarsızlık daha keskin. Aynı gün, örtüşen yazar listeleriyle gönderilen iki
kardeş makale, aynı görevdeki aynı mimariler için uzlaşmaz sayılar veriyor:

| model | Surya makalesi, Tablo 4 | SuryaBench, Tablo 3(b) |
|---|---|---|
| AlexNet | TSS 0.358, HSS 0.398, F1 0.454 | TSS 0.359, HSS 0.354, F1 0.679 |
| ResNet50 | TSS **0.018**, HSS 0.028, F1 0.055 | TSS **0.261**, HSS 0.281, F1 0.627 |

ResNet50'nin TSS'i yaklaşık on dört kat farklı. AlexNet'in F1'i 0.225 farklı.
Hangisinin doğru olduğunu söyleyemeyiz; asıl mesele de bu. Temel modelin
0.436'sı bir referansa göre değerlendiriliyor, ama o referansın kendisi iddia
edilen farktan daha oynak. Bu farkı ne açıklıyorsa — başka bir bölüm, başka bir
eşik, başka bir eğitim koşusu — hiçbir tabloda yazmıyor.

Bir tutarsızlığı daha not ediyoruz, çünkü görevi yeniden üretmek isteyen herkesi
etkiliyor. SuryaBench metni eşiklerinin *"to the equivalent strength of an
M1.0-class flare"* karşılık geldiğini söylüyor ama eşiği 10⁻⁴ W m⁻² olarak yazıyor.
Oysa 10⁻⁴ M1.0 değil, X1.0'dır. Model makalesi 10⁻⁵ W m⁻² (M1.0) kullanıyor.
Belirsizliği etiketlerin kendisine bakarak çözdük: **etiketler M1.0'ı izliyor.**
§2.4'te 128.328 satırın tamamında doğruladık.

### 2.4 Veride bir etiket sızıntısı tuzağı

Yayımlanan CSV dosyalarında `max_goes_class[t]` sütunu, [t, t+24s) aralığındaki
**maksimum** sınıfı veriyor. Yani geçmiş bir gözlem değil, etiketin kaynağı.

`label_max == (max_goes_class ≥ M1.0)` eşitliğini **128.328 satırın 128.328'inde**
doğruladık. Dolayısıyla bu sütunu *t* anında okuyan herhangi bir taban çizgisi
kusursuz sonuç verir ve tamamen anlamsızdır.

Aynısı `cumulative_index` için de geçerli: veri kartı onu da aynı tahmin
penceresi üzerinden tanımlıyor ve `label_cum == (cumulative_index ≥ 10)`
kimliğini 128.328 satırın 128.328'inde doğruladık. Bu çalışmadaki bütün
özellikler t−24s veya daha eski okunuyor. O gecikmede ileriye bakan iki sütun
da [t−24s, t) aralığını kapsıyor, yani tahmin anında meşru olarak bilinebilir
bilgiler oluyor.

### 2.5 İlgili çalışma: kıyaslamanın atladığı yerleşik uygulama

Güneş patlaması tahmininin karşılaştırmalı değerlendirme için zaten bir standardı
var. Barnes ve ark. (2016), 2009'daki kurumlar arası "all-clear" çalıştayını
raporlarken yöntemi kurdu. Vardıkları sonuç şuydu: *"there is no single method that
is clearly better than the others for flare prediction in general"* — genel olarak
patlama tahmininde diğerlerinden açıkça daha iyi olan tek bir yöntem yok. Katılan
hiçbir yöntem iklimsel referanstan belirgin biçimde iyi çıkmamıştı.

Devam serisi ayrı bir toplantıdan doğdu: 2017'de Nagoya Üniversitesi'ndeki ISEE
enstitüsünde. Leka ve ark. (2019a, II. Makale), Leka ve ark. (2019b, III. Makale)
ve Park ve ark. (2020, IV. Makale) yöntemi dünyadaki operasyonel tahmin
sistemlerine uyguladı. Merkezî sonuçları bizim için doğrudan önemli. II.
Makale'nin özetinden:

> *"Numerous methods performed consistently above the 'no skill' level, although
> which method scored top marks is decisively a function of flare event definition
> and the metric used; there was no single winner."*
>
> "Çok sayıda yöntem tutarlı biçimde 'beceri yok' seviyesinin üzerinde performans
> gösterdi. Ancak hangi yöntemin en yüksek notu aldığı, kesin olarak patlama olayı
> tanımına ve kullanılan metriğe bağlı — tek bir kazanan yoktu."

Aynı seri, tek bir sayı vermek yerine iklimsel referansları raporlamayı ve metrik
duyarlılığını incelemeyi de yerleştirdi.

Basit yöntemlerin rekabetçi olduğunu biz keşfetmiş değiliz. O sonuç neredeyse on
yıllık ve §4.2'miz onun yeni bir ortamda tekrar gösterilmesinden ibaret. Bizim
katkımız şu gözlem: 2025'te öne çıkarılarak yayımlanan bir temel model kıyaslaması
**bu yerleşik uygulamalardan ayrılıyor.** İki görüntü modeline karşı tek bir
havuzlanmış TSS veriyor. Görüntüsüz ya da iklimsel referans yok. Değerlendirme
bölümü ve eşik prosedürü yazılmamış. Belirsizlik yok.

Barnes (2016) ve Leka/Park serisine göre okunduğunda, bildirilen karşılaştırma bir
sıralama iddiasını taşıyamaz. Ölçümlerimiz de bu eksikliğin neyi gizlediğini somut
olarak gösteriyor: metriğe göre değişen sıralama (§4.2), örtüşen aralıklar (§4.3),
rejime bölünen beceri (§4.4) ve aktarılamayan kalibrasyon (§4.5).

### 2.6 Araştırmada ve operasyonda referans tahmin

Açık referanslara karşı karşılaştırma bizim tercihimiz değil. Bu alan zaten böyle
çalışıyor ve operasyonel kurum bunu kendi ürününe uyguluyor.

NOAA'nın Uzay Havası Tahmin Merkezi (SWPC) günlük olasılıksal M ve X sınıfı patlama
tahminleri yayımlıyor. Belirli bir 24 saatlik gün için %1'den %99'a yüzdeler, bir
ile üç gün arası öngörü süresiyle. Ve yayımladığı doğrulama, bu tahminlerin
becerisini **30 günlük iklimsel referansa ve 1 günlük kalıcılığa karşı** ölçüyor.
Sabit iklimsel tahmine göre iyileşme yoksa buna "negatif beceri" diyor.

Aynı beklenti araştırma literatüründe de var. Leka ve ark. (2019a), operasyonel
ortamlarda doğru ölçütün *"the best 'unskilled' forecast available"*, yani mevcut en
iyi "becerisiz" tahmin olduğunu savunuyor. TSS'in kendisi de — Hanssen–Kuipers
ayırt edicisi ya da Peirce beceri skoru — yöntemler arası karşılaştırmayı anlamlı
kılmak için standart metrik olarak benimsenmişti (Bloomfield ve ark. 2012).

Son dönemden iki sonuç, belgelediğimiz eksikliği mazur görmeyi zorlaştırıyor.

**Birincisi.** Makine öğrenmesiyle patlama tahminine Bobra & Couvidat'tan (2015)
beri SHARP-parametresi geleneği hâkim. Onlar operasyonel yapılandırmalarında 24
saat içinde ≥M1.0 için 0.76'lık TSS bildiriyor. Bu gelenekteki özellik sıralaması
çalışmaları, önceki patlama etkinliğini tekrar tekrar en güçlü tekil
öngörücüler arasında buluyor (Nishizuka ve ark. 2017; Campi ve ark. 2019). Ve van
der Sande ve ark. (2023), manyetogram verisinden 24 saatlik M sınıfı tahmini
yaparken şu sonuca varıyor:

> *"flaring history has greater predictive power than our CNN-extracted features"*
>
> "patlama geçmişi, CNN ile çıkardığımız özelliklerden daha yüksek tahmin gücüne
> sahip"

Bizim §4.2'miz aynı bulgunun, çok daha büyük bir görüntü modeline karşı tekrar
ortaya çıkmasıdır.

**İkincisi ve daha doğrudan olanı.** Camporeale & Berger (2025), 27 yıllık SWPC
patlama tahminini doğruladı. Buldukları şu: *"even the simple persistence
model—using no training and based solely on the previous day's flare activity—
performs on par with, or only marginally below, the SWPC forecast."* Yani hiçbir
eğitim almayan ve sadece önceki günün patlama etkinliğine bakan basit kalıcılık
modeli bile, resmî SWPC tahminiyle başa baş gidiyor ya da ondan çok az geride
kalıyor. Makaleyi, seve seve kendimizin yazacağı bir tavsiyeyle bitiriyorlar:

> *"Any solar flare forecasting or all-clear prediction models developed in a
> research setting should perform the type of basic forecast verification study
> shown here — using the same baseline models and metrics for comparison — before
> being claimed as an advance over current methods."*
>
> "Araştırma ortamında geliştirilen her patlama tahmini modeli, mevcut yöntemlere
> göre bir ilerleme olduğu iddia edilmeden önce burada gösterilen türde temel bir
> tahmin doğrulaması yapmalıdır — karşılaştırma için aynı taban çizgilerini ve
> metrikleri kullanarak."

Bu tavsiye, değerlendirdiğimiz modelle aynı yıl *Space Weather* dergisinde
yayımlandı. Yani kalıcılığa karşı kontrol etme fikri bize ait değil. Bizim
eklediğimiz şu: bu modeli kimse kontrol etmemişti. Üstelik kıyaslama,
yayımlandığı hâliyle bir okuyucunun kontrol etmesine de imkân vermiyor.

SHARP literatürünü abartmıyoruz. Sadece patlama geçmişine bakan
bir modeli SHARP-parametreli bir modelle eşit koşullarda karşılaştırıp iki skoru da
veren bir çalışma bulamadık ve öyle bir şeyin var olduğunu iddia etmiyoruz. En
yakını van der Sande ve ark. (2023) ve o da patlama geçmişini SHARP skalerleriyle
değil, CNN'in çıkardığı manyetogram özellikleriyle karşılaştırıyor. Kendimiz de bir
SHARP taban çizgisi çalıştırmadık (§7).

## 3. Yöntem

### 3.1 Model değerlendirmesi

Yayımlanan `nasa-ibm-ai4science/solar_flares_surya` kontrol noktasını, yazarların
kendi `infer.py`, `SolarFlareDataset`, `config_infer.yaml` dosyaları ve
ölçekleyicileriyle çalıştırdık. Ham netCDF girdileri resmî S3 arşivinden akıttık:
indir, çıkarım yap, sil. Donanım T4, bf16 otomatik dönüştürme (autocast).
Deterministik çalıştı: tohum 42, karıştırma yok, veri artırma yok.

Puanladığımız her etiketi resmî bölüm CSV'lerine karşı tekrar kontrol ettik:
**739 doğrulama ve 407 test saatinde sıfır uyuşmazlık.** Sabitlenen sürümler:
kontrol noktası `ec7c42a` (18 Ağu 2025), patlama veri kümesi `bf474bc`
(16 Ara 2025; etiket dosyalarının karşılaştırması, bu sürümün yalnızca README'ye
dokunduğunu gösteriyor).

### 3.2 Örnekleme

Tam bölüm çıkarımı çok pahalı. Her tahmin saati ~586 MB'lık iki zaman adımı
istiyor. Bir blok içindeki ardışık saatler bunlardan birini paylaşıyor, o yüzden
örneklemimizi puanlamak **1.224 ayrı netCDF dosyası, kabaca 700 GB** demek oldu.
Sadece tam test bölümünü kapsamak yaklaşık 25 TB gerektirirdi.

Bu yüzden tohumlanmış ve tabakalı bir örneklem çektik: bitişik 24 saatlik
pencerelerden 36'sı doğrulamadan (2011–2019), 20'si testten (2020–2024). Patlama
etkin dönemleri bilerek fazla örnekledik ki yeterince pozitif olsun.

**Eksik arşiv dosyaları bize pahalıya patladı.** Planlanan 864 doğrulama saatinin
125'ini, planlanan 480 test saatinin 73'ünü kaybettik. Her ikisinde de yaklaşık
%15. Üstelik bu boşluklar bazı pencereleri parçaladı: planlanan 36 doğrulama
penceresi 50 bitişik koşu hâlinde kaldı (20'si en az 20 saatlik, 30'u daha kısa
parçalar), 20 test penceresi ise 28 koşu hâlinde (14'ü en az 20 saatlik). Bu makale
boyunca blok dediğimiz şey, bu kurtarılmış bitişik koşulardan biri. Çünkü
saatlerin gerçekten birbirine bağlı olduğu birim bu.

Örneklem taban oranlarımız tam bölüm oranlarından yüksek çıktı: doğrulamada 0.115,
testte 0.327. Yani mutlak değerler tam bölüm sayılarıyla doğrudan karşılaştırılamaz.
Ama bütün model karşılaştırmaları özdeş saatlerde yapılıyor.

**Akıl sağlığı kontrolü.** Ucuz taban çizgileri GPU istemediği için onları hem
örneklemimizde hem eksiksiz bölümlerde çalıştırabildik. Sonuçlar birbirine yakın
çıktı: GOES lojistik 0.685'e karşı 0.661, kalıcılık 0.405'e karşı 0.430. Yani
tabakalama model sıralamasını kayda değer biçimde bozmuyor.

### 3.3 Taban çizgileri

**1. İklimsel (climatology).** Her zaman "patlama yok" de.

**2. Kalıcılık (persistence).** t−24s'te gözlenen etiketi tahmin olarak ver. Bu
etiketi bölüm dosyasından değil, eksiksiz saatlik kayıttan okuyoruz. Böylece
referansı komşu bölüme düştüğü için hiçbir saati atmak zorunda kalmıyoruz.

**3. GOES-geçmişi lojistik regresyon.** t−24s'ten t−168s'e kadar gecikmelerden 11
özellik: her gecikme için logaritmik zirve akı, 7 günlük maksimum ve kümülatif
indeks terimleri. Standartlaştırılmış, L2 düzenlileştirilmiş, resmî eğitim
bölümünde gradyan inişiyle uydurulmuş. 74.760 satırın 74.564'ü kullanıldı; 196'sı
sonlu olmayan özellikler yüzünden düştü (bkz. §7). Bir CPU'da saniyeler içinde
eğitiliyor.

### 3.4 Metrikler ve belirsizlik

TSS (POD − POFD), HSS, F1, tam karışıklık matrisleri ve tam bir eşik taraması
hesaplıyoruz.

Aynı 24 saatlik blok içindeki saatler birbirine sıkı bağlı. Bu yüzden saat başına
yapılan basit önyükleme varyansı olduğundan az gösterir. Biz blokların tamamını
yeniden örnekliyoruz: örneklenmiş saatler için 50 doğrulama ve 28 test bloğu,
eksiksiz bölümler içinse takvim günleri. Yüzdelik %95 aralıkları bildiriyoruz.

Her aralık kendi rastgele sayı üretecini baştan tohumluyor. Yani basılan bir aralık,
kendisinden önce kaç aralık hesaplandığından bağımsız olarak tek başına yeniden
üretilebiliyor.

## 4. Sonuçlar

### 4.1 Eksik taban çizgisi

Tam doğrulama bölümünde kalıcılık kuralı tek başına TSS 0.430 alıyor. Gün bloklu
%95 aralığı **[0.238, 0.621]**. Yani bu aralık, 366 milyon parametreli bir model
için bildirilen 0.436'yı içine alıyor.

0.436'nın yanında hiçbir belirsizlik verilmemiş; dolayısıyla iki sayıyı biçimsel
olarak karşılaştıramayız. Aralığın gösterdiği şu: **sadece sıradan taban
çizgisinin örnekleme değişkenliği bile bildirilen sonucu kapsıyor.** Bir kıyaslama tablosunun göstermesi gereken bilgi tam olarak budur — ve
bu tablo onu göstermiyor.

Tam test bölümünde kalıcılık 0.535 alıyor, aralığı [0.502, 0.568].

### 4.2 Görüntü kullanmayan ucuz bir model, temel modelle başa baş gidiyor

**Eşleştirilmiş karşılaştırma.** Bu bizim birincil sonucumuz, çünkü iki sayı da
aynı tahmin saatlerinden geliyor:

| bölüm | saat | GOES-geçmişi lojistik | Surya (ayarlı) | Surya @0.5 |
|---|---|---|---|---|
| doğrulama | 739 | **0.685** | 0.673 | 0.425 |
| test | 407 | **0.738** | 0.632 | 0.173 |

Doğrulamada ikisi ayırt edilemiyor. Testte ucuz model her metrikte önde: HSS
0.699'a karşı 0.571, F1 0.807'ye karşı 0.735. TSS'teki eşleştirilmiş blok
önyüklemesi farkı da sıfırı dışlıyor, ama kıl payı (+0.106, %95 GA [+0.009,
+0.280]; §4.3). Her iki eşik de örneklem içinde
ayarlandı, yani bu ikisini de eşit ölçüde kayırıyor.

**Eşleştirilmemiş karşılaştırma.** Taban çizgileri GPU istemediği için onları her
resmî saatte de çalıştırabildik. Kiraz toplamayı önleyen bir protokol kullandık:
ağırlıklar eğitim bölümünden geliyor, tek bir eşik tam doğrulama bölümünde seçilip
(0.10) test için donduruluyor.

| bölüm | n | taban | model | TSS | %95 GA | HSS | F1 |
|---|---|---|---|---|---|---|---|
| doğrulama (tam) | 3.672 | 0.109 | **GOES lojistik** | **0.661** | [0.532, 0.777] | 0.375 | 0.475 |
| doğrulama (tam) | 3.672 | 0.109 | kalıcılık | 0.430 | [0.238, 0.621] | 0.428 | 0.491 |
| test (tam) | 43.848 | 0.294 | **GOES lojistik** | **0.554** | [0.526, 0.581] | 0.436 | 0.655 |
| test (tam) | 43.848 | 0.294 | kalıcılık | 0.535 | [0.502, 0.568] | 0.536 | 0.672 |

§2.3 bildirilen bölüm için üç aday bıraktığı için, ucuz taban çizgisini üçünde de
çalıştırdık. Model makalesinin bölümlemesinde (2011–2019'un 15–31. günleri, yani
tam olarak doğrulama bölümü) 0.661 alıyor. Veri kartınınkinde (2020–2024) 0.554
alıyor. SuryaBench'inkinde (sadece 2020) 0.452 alıyor (§4.6). **Üçü de 0.436'yı
geçiyor.** Yani iddiamız belirsizliğin çözülmesine bağlı değil. Üstelik doğrulamada
ucuz modelin kendi aralığı bildirilen değeri dışarıda bırakıyor.

**Bu karşılaştırmayı yine de eşleştirilmemiş olarak işaretliyoruz.** Taban çizgisi
bütün saatlerde çalıştı, model bizim örneklemimizde. Ve 0.436 bizim değil,
yazarların kendi ölçümü. Bunu yukarıdaki eşleştirilmiş sonucun destekçisi olarak
sunuyoruz, birincil iddia olarak değil. Gün bloklu aralıklar blok birimine de
dayanıklı: 2 ve 3 günlük bloklarla doğrulama kalıcılık aralığı 0.436'yı içermeye,
doğrulama GOES aralığı onu dışlamaya devam ediyor (`gaps_audit.py`).

**Üstünlük metriğe bağlı.** Tam doğrulama bölümüne bakarsak,
bildirilen HSS (0.522) ve F1 (0.561) ucuz taban çizgisinin 0.375 ve 0.475
değerlerini geçiyor. Çünkü taban çizgisi TSS'ini yüksek yanlış alarmla satın alıyor:
355 isabete karşı 740 yanlış alarm.

Bu yüzden "ucuz model her açıdan üstün" demiyoruz. Dediğimiz daha dar bir şey:
bu literatürün standardı olan ve taban orandan etkilenmeyen metrikte, yani
**TSS'te**, görüntü modalitesi bu görevde X-ışını geçmişine karşı ölçülebilir bir
avantaj göstermiyor. Eşleştirilmiş test saatlerinde ise ucuz model üç metrikte
birden önde.

### 4.3 Tek sayılı karşılaştırmalar yetersiz güçte

*(Şekil 3: karar eşiğine göre TSS, taban çizgileri referans olarak.)*

Ölçtüğümüz saatlerde, blok önyüklemesiyle:

| bölüm | model | TSS | %95 GA | genişlik |
|---|---|---|---|---|
| doğrulama | Surya @0.5 | 0.425 | [0.028, 0.746] | 0.72 |
| doğrulama | Surya @0.16 (ayarlı) | 0.673 | [0.289, 0.886] | 0.60 |
| doğrulama | kalıcılık | 0.405 | [−0.019, 0.792] | 0.81 |
| doğrulama | GOES lojistik @0.10 | 0.685 | [0.417, 0.881] | 0.46 |
| test | Surya @0.5 | 0.173 | [0.000, 0.484] | 0.48 |
| test | Surya @0.04 (ayarlı) | 0.632 | [0.315, 0.876] | 0.56 |
| test | kalıcılık | 0.618 | [0.258, 0.889] | 0.63 |
| test | GOES lojistik @0.34 | 0.738 | [0.467, 0.940] | 0.47 |

Aralıklar 0.46–0.81 TSS genişliğinde. Ama tekil aralıkların örtüşmesi, fark
hakkında zayıf bir kanıttır; aynı yeniden örneklenen bloklar iki skoru birlikte
oynatır. Bu yüzden çiftleri de yeniden örnekledik: her çekilişte tek bir blok
örneklemi bütün yöntemleri puanlıyor ve ayrışmaya, eşleştirilmiş farkın aralığı
karar veriyor (`paired_diff.py`; 4.000 çekiliş; eşikler tam örneklem
değerlerinde sabit).

| bölüm | eşleştirilmiş fark | ΔTSS | %95 GA |
|---|---|---|---|
| doğrulama | GOES lojistik − Surya (ayarlı) | +0.012 | [−0.325, +0.473] |
| doğrulama | Surya (ayarlı) − kalıcılık | +0.268 | [−0.153, +0.658] |
| doğrulama | GOES lojistik − kalıcılık | +0.279 | [−0.058, +0.681] |
| doğrulama | Surya @0.5 − kalıcılık | +0.019 | [−0.398, +0.427] |
| test | GOES lojistik − Surya (ayarlı) | **+0.106** | **[+0.009, +0.280]** |
| test | Surya (ayarlı) − kalıcılık | +0.014 | [−0.210, +0.253] |
| test | GOES lojistik − kalıcılık | +0.120 | [−0.009, +0.330] |
| test | Surya @0.5 − kalıcılık | **−0.445** | **[−0.825, −0.086]** |

On eşleştirilmiş farkın sekizi sıfırı kapsıyor (§4.4'teki iki hibrit çifti de
kapsıyor). Kapsamayan ikisi öğretici. Ucuz modelin testte ayarlı Surya'ya karşı
üstünlüğü sıfırı ancak kıl payı dışlıyor (alt sınır +0.009); bunu kesin değil,
işaret niteliğinde sayıyoruz. Çalışmadaki en güçlü ayrışma ise olumsuz yönde:
**model, sevk edilen 0.5 eşiğinde test penceresinde 24 saatlik kalıcılığın
anlamlı şekilde altında kalıyor** (−0.445, [−0.825, −0.086]).

Ama iki dışlama da, on karşılaştırma aynı anda koşarken geleneksel %95
düzeyinde yapılıyor ve ikisi de bu hesabı atlatamıyor: önyükleme kuyruk
oranları %0.55 ve %0.70 — on yönlü Bonferroni'nin istediği %0.25'in üstünde,
ve düzeltilmiş %99.5 aralıkları ya sıfıra değiyor ([0.000, +0.382]) ya sıfırı
geçiyor ([−0.924, +0.070]) (`gaps_audit.py`). Bu yüzden sevk edilen eşiğin
açığını koşulsuz değil, çalışmanın en güçlü ayrışması olarak niteliyoruz. En
net farkımızın bile aile düzeltmesini geçememesi, aslında (i) bulgusunun
kendisidir: 50 ve 28 blokla bu protokol neredeyse hiçbir şeyi çözemiyor.

Bu büyüklükte farkların neden gerektiği, saat yerine blok saydığımızda ortaya
çıkıyor: 50 doğrulama bloğunun sadece
**6'sında pozitif var**, 28 test bloğunun sadece 11'inde. TSS'in isabet oranı
terimini yalnızca pozitif içeren bloklar belirliyor. Yani yayımlanmış her patlama
tahmini TSS'inin arkasındaki gerçek örneklem, yanına yazılan saat sayısının
düşündürdüğünden çok daha küçük.

**Öneriyoruz: böyle her skorun yanında, pozitif içeren bağımsız blok sayısı da
yazılsın.** Tek satırlık bir ekleme ve aşırı yorumların çoğunu engeller.

### 4.4 Beceri rejime bölünmüş görünüyor, sıradan bir melez kazanıyor

*(Şekil 4: rejime göre yakalama oranları.)*

Pozitifleri kalıcılık referansına göre ayırdığımızda:

| | doğrulama | test |
|---|---|---|
| başlangıç pozitifleri (kalıcılık kör) | 46 | 27 |
| devam pozitifleri | 39 | 106 |
| sönme saatleri (kalıcılık yanlış alarm) | 35 | 49 |
| yakalanan başlangıç — kalıcılık | 0/46 | 0/27 |
| yakalanan başlangıç — Surya (ayarlı) | 35/46 | 13/27 |
| yakalanan başlangıç — Surya @0.5 | 14/46 | 0/27 |
| sönme yanlış alarmı — kalıcılık | 35/35 | 49/49 |
| sönme yanlış alarmı — Surya (ayarlı) | 10/35 | 38/49 |

İki sütun türce farklı. Kalıcılık sütunu istatistiksel bir sonuç
değil. t−24s'teki etiketi kopyalayan bir kural, henüz başlamamış bir epizodu
işaretleyemez. Sönmekte olan bir epizodun da her saatini işaretlemek zorundadır.
Bunlar tanım gereği böyle ve örneklem ne kadar büyürse büyüsün değişmez.

Modelin başlangıç davranışı ise başka bir mesele ve sınırları ağır. 46
doğrulama ve 27 test başlangıç saati, sadece **4 ve 3 bağımsız bloğa** dağılıyor.
Yani elimizde bir başlangıç örneklemi değil, bir avuç patlama epizodu var. Yakalama
oranı için hesapladığımız aralıklar da buna göre işe yaramaz çıkıyor:

| bölüm | öngörücü | yakalanan | oran | %95 GA | isabet olan blok |
|---|---|---|---|---|---|
| doğrulama | Surya @0.16 (ayarlı) | 35/46 | 0.761 | [0.357, 1.000] | 4/4 |
| doğrulama | Surya @0.50 (sevk edilen) | 14/46 | 0.304 | [0.000, 0.750] | 3/4 |
| test | Surya @0.04 (ayarlı) | 13/27 | 0.481 | [0.000, 1.000] | 2/3 |
| test | Surya @0.50 (sevk edilen) | 0/27 | 0.000 | [0.000, 0.000] | 0/3 |

Son satır yanlış okumaya davetiye çıkarıyor. 0/27
gözleminin etrafındaki [0.000, 0.000] aralığı bir sınır artefaktıdır. Hiç başarı
içermeyen bir örneklemi yeniden örneklerseniz zaten hep sıfır çıkar. Bu kesinlik
kanıtı değildir.

Sıfır sayım için doğru ifade, etkin örnekleme uygulanan üçler kuralıdır. Üç
başlangıç bloğuyla %95 üst sınırı 3/3 ≈ 1.0 çıkar. Yani hiçbir şey kısıtlamaz.

Bu yüzden başlangıç sonuçlarını **bir avuç epizot üzerinde betimsel gözlem olarak
bildiriyoruz, oran tahmini olarak değil.** Örneklenen üç test epizodunda model, sevk
edilen eşiğinde 27 saatin hiçbirini işaretlemedi. Ayarlı bir eşikte ise üç epizodun
ikisinde saat işaretledi. Gözlem çarpıcı ve daha büyük ölçekte kontrol
edilmeye değer, ama ölçülmüş bir kaçırma oranı değil.
Aynı çekince doğrulama sütunu için de geçerli; orada ayarlı eşik dört epizodun
hepsinde saat işaretliyor.

Yine de iki öngörücü rakip değil, birbirini tamamlıyor. Ve bu ifade başlangıç
sayımlarına değil, havuzlanmış skora dayanıyor: `kalıcılık VEYA Surya` doğrulamada
TSS **0.705** alıyor. Her iki bileşenin de üstünde (0.673 ve 0.405) — ama bu
bir nokta tahmini sıralaması; güçlü bileşene karşı eşleştirilmiş fark sıfırı
kapsıyor (+0.032, [−0.044, +0.241]).

### 4.5 Kalibrasyon rejime bağlı ve aktarılamıyor

*(Şekil 1: güvenilirlik diyagramları, doğrulama ve test.)*

Aşağıda eksiksiz güvenilirlik tabloları var; her kutuya kaç bağımsız bloğun
katkı verdiğini de yazdık.

**Doğrulama (2011–2019), Brier 0.057**

| kutu | n | blok | ortalama öngörü | gözlenen |
|---|---|---|---|---|
| [0.00, 0.01) | 391 | 32 | 0.002 | 0.000 |
| [0.01, 0.05) | 110 | 20 | 0.024 | 0.118 |
| [0.05, 0.10) | 48 | 15 | 0.076 | 0.062 |
| [0.10, 0.25) | 88 | 15 | 0.172 | 0.125 |
| [0.25, 0.50) | 58 | 11 | 0.350 | 0.362 |
| [0.50, 0.75) | 18 | 4 | 0.622 | 0.667 |
| [0.75, 1.01) | 26 | 3 | 0.866 | 0.962 |

**Test (2020–2024), Brier 0.208**

| kutu | n | blok | ortalama öngörü | gözlenen |
|---|---|---|---|---|
| [0.00, 0.01) | 180 | 15 | 0.003 | 0.078 |
| [0.01, 0.05) | 41 | 8 | 0.021 | 0.049 |
| [0.05, 0.10) | 35 | 13 | 0.078 | 0.657 |
| [0.10, 0.25) | 108 | 13 | 0.170 | 0.537 |
| [0.25, 0.50) | 20 | 9 | 0.307 | 0.650 |
| [0.50, 0.75) | 1 | 1 | 0.504 | 1.000 |
| [0.75, 1.01) | 22 | 1 | 0.931 | 1.000 |

İki tablo da tam hâliyle veriliyor, sadece işimize gelen satırlar değil. İkisi de §3.2'nin tabakalamasını miras alıyor: patlama-etkin pencereler
fazla temsil edildiği için gözlenen sıklık her kutuda yukarı çekiliyor. Yani
iki pencere birbiriyle karşılaştırılabilir, ama ikisi de tam bölüm kalibrasyon
ölçümü değil (§7).

Doğrulama kalibrasyonu iyi ama kusursuz değil: [0.01, 0.05) kutusu yaklaşık
beş kat düşük güvenli ve bu sapma test başarısızlığıyla aynı yönde. Yani iki
pencere arasındaki fark türden çok derece farkı. Ama derece büyük, ve testte
kalibrasyon bozukluğu operasyonel kararların gerçekten alındığı kutulara kadar
ulaşıyor.

İki çekince daha buraya ait. Modelin kusursuz göründüğü test [0.75, 1.01) kutusu
**tek bir bloktan** geliyor. [0.50, 0.75) kutusu ise tek bir saat içeriyor.

En sağlam ifademiz birleştirilmiş [0.05, 0.25) bandı: 15 bağımsız blok boyunca 143
test saati, ortalama öngörü 0.148, gözlenen sıklık 0.566. Bu bandın içinde blok
başına gözlenen sıklıklar iki uçta toplanıyor: beş blok 1.00'da, beş blok 0.00'da.
Bu da hatanın düzgün değişen değil, epizodik bir hata olduğuna işaret ediyor.

Doğrulamada uydurduğumuz tek parametreli Platt düzeltmesi a ≈ 0.944, b ≈ 0.145
veriyor. Yani neredeyse hiçbir şey yapmayan bir eşleme. Test TSS'i 0.173'te
değişmeden kalıyor; Brier sadece 0.208'den 0.198'e iniyor.

Sonuç şu: kalibrasyon bozukluğu, dağılım içi veriden düzeltilebilecek sabit bir
model yanlılığı değil. Gözlem rejimine bağlı bir kayma.

### 4.6 Ortak neden: taban oranının durağan olmaması

*(Şekil 2: yıl bazında pozitif oranı ve sabit eşikte TSS.)*

Eşiği doğrulamada dondurup yıl bazında baktığımızda:

| yıl | n | taban oranı | GOES lojistik TSS | kalıcılık TSS |
|---|---|---|---|---|
| 2020 | 8.784 | 0.0055 | 0.452 | −0.005 |
| 2021 | 8.760 | 0.0613 | 0.514 | 0.270 |
| 2022 | 8.760 | 0.2638 | 0.250 | 0.322 |
| 2023 | 8.760 | 0.4435 | 0.056 | 0.293 |
| 2024 | 8.784 | 0.6969 | 0.079 | 0.389 |

Pozitif oranı bölüm boyunca **128 kat** artıyor: 0.0055'ten 0.6969'a. İki yöntem
buna zıt yönlerde tepki veriyor: sabit eşikli lojistik 2021'deki 0.514'ten
2024'te 0.079'a çöküyor, kalıcılık ise −0.005'ten 0.389'a tırmanıyor. Ama ikisi
de havuzlama yanılsamasından kaçamıyor. Havuzlanmış test TSS'i lojistik için
0.554, yıllık aralığı 0.056–0.514; kalıcılık için 0.535, yıllık aralığı −0.005
ile 0.389. İkisinde de havuzlama, hiçbir tekil yılda görülmeyen bir beceri
üretiyor.

Yani havuzlama, olmayan bir beceriyi varmış gibi gösteriyor.

## 5. Tartışma

### 5.1 Ucuz bir taban çizgisi olmadan modalitenin katkısı ölçülemez

Bir patlama kıyaslamasının cevaplaması gereken soru "bu model kaç puan alıyor?"
değil. Doğru soru şu: **"güneş görüntüleri, zaten yapabildiğimizin üstüne ne
katıyor?"**

Bu soru ancak değerlendirmede görüntü kullanmayan bir şey varsa cevaplanabilir.
Oysa bildirilen karşılaştırma Surya'yı AlexNet ve ResNet50'ye karşı koyuyor ve
ikisi de aynı görüntüleri tüketiyor. Yani tablodaki her satır test edilen
modaliteyi zaten paylaşıyor. Görüntünün katkısı karşılaştırmadan sadeleşip gidiyor.

Bizim sonuçlarımız bu görevde o katkının küçük ya da yok olduğunu düşündürüyor.
**On bir katsayılı, tek girdi kanallı bir model onunla başa baş gidiyor.**

Bunu önceden eğitilmiş omurga hakkında bir hüküm olarak okumamak gerekir. Bu, tek
bir ikili aşağı akış görevi hakkında bir hüküm. Makul bir açıklama şu olabilir: 24
saat içinde M sınıfı patlama olup olmayacağı, büyük ölçüde Güneş'in zaten
patlama yapıp yapmadığına bağlı. O bilgi de tamamen X-ışını kaydının içinde.

Eğer öyleyse, bu görev bir güneş temel modelinin ne bildiğini ölçmek için kötü bir
araç. Daha iyi araçlar var: uzamsal çözünürlüklü ürünler, daha uzun ufuklarda öngörü
süresi eğrileri, oluşum yerine büyüklük tahmini, ya da modelle birlikte yayımlanan
diğer görevlere aktarım. Ucuz özelliklerin ulaşamadığı yerde değer göstermek, ucuz
özelliklerin ulaştığı yerde marjinal bir galibiyetten çok daha güçlü bir iddia olur.

### 5.2 Durağan olmayan taban oranı, havuzlanmış metrikleri yanıltıcı kılar

Güneş döngüsü bu problemdeki en büyük karıştırıcı değişken. Resmî test bölümü de
tam onun dik yükseliş evresini kapsıyor.

Pozitif oranındaki 128 katlık değişim şu anlama geliyor: 2020 görevi ile 2024
görevi istatistiksel olarak farklı problemler. Sadece aynı etiket tanımını
paylaşıyorlar. Bunları havuzlamak, hiçbir tekil yılda görülmeyen bir sayı (0.554)
üretiyor. Bu bir modelleme hatası değil, ortak değişken kayması boyunca
toplulaştırmadan doğan bir Simpson paradoksu. O tek sayıyı bildirmek, tam da yanlış
çıkarımı davet ediyor.

Aynı mekanizma kalibrasyon sonucunu da açıklıyor. Patlamalar seyrekken olasılıkları
gerçeğe uygun olan bir model, patlamalar sıklaştığında sistematik olarak düşük
güvenli hâle geliyor. Platt düzeltmesinin aktarılamaması da bunun sabit bir yanlılık
olmadığını, rejimin bir fonksiyonu olduğunu gösteriyor.

Pratikte bu şu demek: sahaya alınan her sistem ya çevrimiçi yeniden kalibre olmalı,
ya da döngü evresine açıkça koşullanmalı. **Güneş minimumunda onaylanmış bir
kalibrasyon, güneş maksimumu hakkında kanıt sayılmaz.**

Bu sorun helyofiziğe özgü de değil. Yavaş döngüsel bir sürücüsü olan her seyrek olay
kıyaslaması aynı şekilde değerlendirilirse şişmiş havuzlanmış metrikler ve
aktarılamayan kalibrasyon üretir. Mevsimsel epidemiyoloji, orman yangını riski, bazı
finansal rejimler. Çözüm daha fazla veri değil, tabakalı raporlama.

### 5.3 Tamamlayıcılık, sıralamadan daha yararlı

Rejim bölünmemiz iki öngörücünün ayrı yerlerde başarısız olduğunu gösteriyor.
Kalıcılık, ilke olarak bile, başlamamış bir epizodu göremez ve epizot sönerken
zorunlu olarak yanlış alarm verir. Bu iki ifade tanım gereği doğru.

Örneklemimizde model bu kör noktanın bir kısmını kapatıyor. Ama §4.4'ün ısrarla
söylediği gibi, bunu oran olarak veremeyeceğimiz kadar az epizot var. Üstelik
sadece sevk edilenden çok daha düşük eşiklerde oluyor.

Nicel olarak savunabileceğimiz şey havuzlanmış sonuç: **ikisinin birleşimi her iki
bileşeni de geçiyor.** Operasyonel bir kullanıcı için asıl işe yarar bulgu budur.
Ortalamada hangi tahmincinin daha iyi olduğu değil, sıradan bir birleşimin yapısal
bir kör noktayı kapattığı. Bu ayrıca şunu düşündürüyor: modelleri sıra hâlinde
listeleyen kıyaslama tabloları, daha değerli bilgiyi gizliyor. O bilgi de her
yöntemin becerisinin nerede yaşadığı.

### 5.4 Belirsizlik isteğe bağlı değil

Elimizde 50 ve 28 bağımsız tahmin bloğu var ve bunların sadece 6'sı ile 11'i
pozitif içeriyor. Bu koşullarda %95 aralıkları 0.46 ile 0.81 TSS arasında uzanıyor.

Yöntemler arasındaki 0.05–0.10'luk farklar, yani kıyaslama tablolarının göstermek
için kurulduğu farklar, bu örneklem büyüklüğünde çözünmüyor. On eşleştirilmiş
karşılaştırmamızda en büyük fark olan 0.445'lik uçurum bile aile düzeltmesini
geçemiyor (§4.3).

Aralıksız nokta tahmini bildirmek, olmayan bir hassasiyet izlenimi veriyor. Standart
örnek başına önyükleme ise blok içi bağı görmezden gelip varyansı olduğundan az
göstererek durumu daha da kötüleştiriyor. Bloklu yeniden örnekleme hiçbir maliyet
getirmiyor ve rutin hâline gelmeli.

## 6. Öneriler

**1.** Her derin modelin yanında **iklimsel, kalıcılık ve istatistiksel (görüntüsüz)
bir taban çizgisi** bildirin. Bu yeni bir talep değil: NOAA SWPC kendi patlama
tahminlerini 30 günlük iklimsel referansa ve 1 günlük kalıcılığa karşı doğruluyor.
Camporeale & Berger (2025) de araştırma modellerinden tam olarak bunu istiyor,
"mevcut yöntemlere göre bir ilerleme olduğu iddia edilmeden önce".

**2.** Değerlendirme bölümünü, yılları ve eşik seçim prosedürünü yazın.

**3.** Yıl ya da rejim bazlı metrik verin. Havuzlanmış sayı veriyorsanız
tabakalı değerleri de yanına koyun.

**4.** Belirsizliği örnek başına değil, zamansal bloklu yeniden örneklemeyle
hesaplayın ve pozitif içeren blok sayısını yazın.

**5.** Güvenilirlik diyagramı yayımlayın. Güneş döngüsü evreleri arasında
kalibrasyon aktarımını ayrı bir değerlendirme ekseni sayın.

**6.** **Makaleyi, kardeş kıyaslama makalesini, model kartını ve veri kartını
birbiriyle ve yayımlanan dosyalarla tutarlı tutun.** Olay eşiğini geçtiği her yerde
sayı olarak yazın. §2.3'teki tutarsızlıkların hepsi, dört belgeyi veriyle
karşılaştıran tek bir kontrol geçişiyle yakalanırdı.

## 7. Sınırlamalar

**Örneklem.** Model puanlaması tam bölümleri değil, tabakalı 1.146 saatlik bir
örneklemi kullanıyor. Mutlak değerler örnekleme bağlı. §3.2'deki akıl sağlığı
kontrolü bunu hafifletiyor.

**Kalibrasyon ve tabakalama.** Güvenilirlik tabloları modelin verdiği olasılığa
koşullanıyor; ama örnekleme patlama-etkin pencereleri fazla temsil ettiği için
gözlenen sıklık her kutuda tam bölümlere göre şişkin. Doğrulama–test karşıtlığı
aynı örnekleme altında hesaplandığı için ayakta; "doğrulamada gerçeğe yakın"
gibi mutlak ifadeler ise örnekleme koşullu. §3.2'deki kontrol TSS'i kapsıyor,
kalibrasyonu değil.

**Ayarlı eşikler.** §4.3–4.5'te hem Surya'nın hem taban çizgisinin eşikleri örneklem
içinde optimize edildi. Bu ikisini de kayırıyor. §4.2'nin tam bölüm protokolü ise
eşiği doğrulamada dondurup öyle kullanıyor.

**Eşleştirilmemiş sayılar.** Tam bölüm taban çizgisi sonuçları bizim model
ölçümlerimizle eşleştirilmiş değil. Onları destekliyorlar ama §4.2'deki
eşleştirilmiş karşılaştırmanın yerini tutmuyorlar.

**Başlangıç sonuçları.** Bu ifadeler 4 ve 3 bağımsız bloğa dayanıyor. Bu etkin
örneklem büyüklüğünde hiçbir başlangıç oranı tahmin edilemez — sıfır yakalama
gözlemi de dahil. §4.4 tam bu yüzden onları betimsel olarak bildiriyor.

**Kendi sınırımız.** Ana skor tablomuz bile 6 (doğrulama) ve 11 (test) pozitif
içeren bloğa dayanıyor. **Bizim sayılarımız da belgelediğimiz sınırlamayı miras
alıyor.** Her birini bir aralıkla birlikte vermemizin sebebi bu.

**Eksik arşiv dosyaları.** Planlanan saatlerin yaklaşık %15'ini kaybettik: 864
doğrulamanın 125'i, 480 testin 73'ü. Bu boşluklar bazı 24 saatlik pencereleri daha
kısa koşulara böldü. Her kurtarılmış koşuyu yeniden örnekleme birimi saydığımız için
bu parçalanma aralıklara yansıyor, gizlenmiyor. Ama bloklarımızın tekdüze 24 saatlik
olmadığı da doğru.

**Düşen eğitim satırları.** 74.760 eğitim satırının 196'sı (%0.26) sonlu olmayan
özellikler yüzünden düştü. Kaynağı, yayımlanan kayıtta GOES sınıfı `A0.0` olan dört
saat. Bu saatlerin logaritmik akısı −∞ çıkıyor ve her biri en fazla yedi gecikmeli
özelliğe yayılıyor.

**bf16 hassasiyeti.** Çıkarım bf16 otomatik dönüştürmeyle yapıldı. Doğrulayıcı bir
fp32 koşusu için GPU erişimimiz yoktu. Bu yüzden açık bırakmak yerine, böyle bir
koşunun neyi değiştirebileceğini sınırladık (`precision_sensitivity.py`).

Sevk edilen 0.5 eşiğinde **iki bölümde de hiçbir saat karar sınırının 10⁻³
yakınında değil.** En yakınları 0.0059 (doğrulama) ve 0.0039 (test) uzakta. 10⁻²
içindeki her saati kasten kötü tarafa çevirdiğimiz düşmanca senaryoda bile TSS en
fazla 0.002 ve 0.008 oynuyor. Ayarlı eşiklerde en kötü durum 0.033. Bizim
aralıklarımız 0.46–0.81 genişliğinde olduğu için bu oynamalar önemsiz kalıyor.

§4.4'ün sıfır yakalama gözlemi daha da güvenli: 27 test başlangıç saati arasındaki
en yüksek olasılık 0.332, yani eşiğin 0.168 altında. Doğrulayıcı bir fp32 koşusu
hâlâ istenir bir şey. Ama buradaki hiçbir sonuç ona bağlı değil.

**SHARP taban çizgisi yok.** Manyetogram türevli bir SHARP taban çizgisi
çalıştırmadık. GOES-geçmişi modeli daha zayıf bir bilgi kümesi kullanıyor, ki bu
argümanı zayıflatmıyor, güçlendiriyor.

**Kalıcılık referansı.** Kalıcılık referansımız bölüm dosyası yerine eksiksiz
saatlik kaydı okuyor. Bu sayede, bölüm içi arama yapsak düşecek üç doğrulama saatini
koruyoruz. Seçim, bildirilen hiçbir skoru üç ondalık basamakta değiştirmiyor.

## 8. Yeniden üretilebilirlik

Bütün olasılıklar, etiketler, kod ve çıktılar yayımlandı:

| dosya | ne yapıyor |
|---|---|
| `heliofloor_data.py` | kanonik yükleyici, metrikler, blok önyüklemesi — diğer her şey bunu kullanıyor |
| `heliofloor_colab.py` | çıkarım koşucusu (GPU; olasılıkları baştan üretiyor) |
| `goes_baseline.py` | Surya'ya karşı eşleştirilmiş saat karşılaştırması |
| `full_split_baseline.py` | eksiksiz bölüm taban çizgileri, dondurulmuş eşik protokolü |
| `analysis_pack.py` | skor tabloları, kalibrasyon, aktarım, rejim bölünmesi, yıl bazında |
| `block_support.py` | her iddianın arkasındaki bağımsız blok desteği |
| `onset_ci.py` | başlangıç yakalama oranları ve üçler kuralı düzeltmesi |
| `paired_diff.py` | yöntemler arası eşleştirilmiş blok-önyükleme farkları |
| `make_figures.py` | `figures/` içindeki dört şekil |
| `verify_paper.py` | makaledeki her iddiayı yeniden hesaplayıp geçti/kaldı basıyor |
| `probs_*.csv` (üç dosya) | 1.146 puanlanmış saat |

Blok planları 42 tohumundan birebir yeniden üretiliyor. Her önyükleme aralığı çağrı
başına yeniden tohumlandığı için, çalıştırma sırasından bağımsız olarak aynı sonucu
veriyor. Puanlanmış olasılıklar depoda hazır durduğu için **bütün analiz bir CPU'da
dakikalar içinde tekrarlanabiliyor.** GPU da gerekmiyor, yeniden çıkarım da.
Kod ve veri: https://github.com/kadircanyildirm-crypto/heliofloor.

## Kaynakça

İngilizce sürümdeki liste aynen geçerli (`PAPER_DRAFT.md`, "References"). Künyeler
27 Ağustos 2026'da Crossref ve arXiv tam metninden doğrulandı.

İki ayrıntı literatürde sık yanlış alıntılanıyor, bizde doğru hâliyle duruyor:
**III. Makale ApJS değil, ApJ'dir** (881(2), 101). Ve **IV. Makale'nin ilk yazarı
Leka değil, Park'tır** (890(2), 124).

## Teşekkür ve beyan

Analiz kodu ve metin taslağı için yapay zeka destekli bir kodlama asistanından
yararlanılmıştır. Tüm sonuçlar depodaki betiklerle üretilmiş, bildirilen her sayı
`verify_paper.py` ile yeniden hesaplanmış ve birincil kaynaklara karşı yazar
tarafından doğrulanmıştır.
