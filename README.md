# Elite Screen Recorder

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1F6FEB?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Recording-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-555555?style=for-the-badge)
![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)

> Modern, hafif ve Windows / Linux / macOS üzerinde çalışması hedeflenen Python tabanlı ekran kayıt uygulaması.

## 📌 Proje Hakkında

**Elite Screen Recorder**, masaüstü ekranını video olarak kaydetmek için hazırlanmış modern bir Python GUI uygulamasıdır.

Uygulama; arayüz için **CustomTkinter**, görüntü işleme/kayıt pipeline'ı için **FFmpeg**, mikrofon yönetimi için **sounddevice** ve görsel işlemler için **Pillow** kullanır. Kaynak kodunda 720p'den 8K'ya kadar çözünürlük seçenekleri, 15/24/30/60 FPS seçenekleri, mikrofon ve sistem sesi desteği, ekran/pencere seçimi ve otomatik çıktı klasörü oluşturma gibi işlevler tanımlanmıştır.

## ✨ Öne Çıkan Özellikler

- 🎥 Ekran kaydı
- 🖥️ Birden fazla ekranı algılama
- 🪟 Windows'ta görünür pencere listesini algılama
- 📐 720p / 1080p / 1440p / 4K / 8K seçenekleri
- 🎞️ 15 / 24 / 30 / 60 FPS seçenekleri
- 🎙️ Mikrofon kaydı
- 🔊 Sistem sesi kaydı
- 🎚️ Video ve ses kayıt seçeneklerini ayrı yönetme
- ⏱️ Kayıt süresi sayacı
- 🔴 Kayıt durumu göstergesi
- 🟣 Modern koyu temalı CustomTkinter arayüzü
- ✨ Hover / glow tabanlı görsel efektler
- 📁 Kayıt klasörünü otomatik oluşturma
- 🪟 Windows'ta FFmpeg konsol penceresini gizleme
- 📦 Eksik Python paketlerini başlangıçta otomatik kurmayı deneme
- ⚙️ FFmpeg'i sistemde arama
- 📥 FFmpeg bulunamazsa işletim sistemine göre otomatik kurulum denemesi
- 🛡️ Windows'ta yönetici yetkisiyle yeniden başlatma desteği

Kaynak kodundaki uygulama sabitleri çözünürlük seçeneklerini `1280x720`, `1920x1080`, `2560x1440`, `3840x2160` ve `7680x4320`; FPS seçeneklerini ise `15`, `24`, `30` ve `60` olarak tanımlar. fileciteturn272file0

## 🧰 Teknoloji Kartları

| Teknoloji | Kullanım |
|---|---|
| 🐍 **Python** | Uygulama mantığı |
| 🎨 **CustomTkinter** | Modern masaüstü kullanıcı arayüzü |
| 🖼️ **Pillow** | Görsel işleme / GUI görselleri |
| 🎙️ **sounddevice** | Ses cihazı ve mikrofon desteği |
| ⚙️ **FFmpeg** | Ekran, video ve ses kayıt pipeline'ı |
| 🪟 **Windows API / ctypes** | Ekran, pencere ve Windows GUI işlemleri |
| 🧵 **threading** | Kayıt ve uzun süren işlemleri GUI'den ayırma |
| 📁 **pathlib** | Çıktı klasörü ve dosya yönetimi |

## 🖥️ Platform Desteği

| Platform | Durum |
|---|---|
| 🪟 Windows | Birincil hedef; Windows API ve DirectShow entegrasyonları bulunur |
| 🐧 Linux | Temel platform desteği hedeflenmiştir; FFmpeg sistemden sağlanır |
| 🍎 macOS | Temel platform desteği hedeflenmiştir; FFmpeg Homebrew üzerinden sağlanabilir |

> Bazı özellikler işletim sistemine özgüdür. Özellikle Windows'taki ekran, pencere ve mikrofon cihazı algılama kodları Windows API / DirectShow davranışlarına bağlıdır.

## 📦 Gereksinimler

- Python 3.10 veya üzeri önerilir
- FFmpeg
- `customtkinter`
- `pillow`
- `sounddevice`

Python paketlerini manuel kurmak için:

```bash
pip install customtkinter pillow sounddevice
```

## 🚀 Kurulum

Repository'yi klonlayın:

```bash
git clone https://github.com/ebubekirbastama/elite-screen-recorder.git
cd elite-screen-recorder
```

Gerekli Python paketlerini kurun:

```bash
pip install customtkinter pillow sounddevice
```

Ardından uygulamayı çalıştırın:

```bash
python "Ekran Kayıt Programı.py"
```

## ⚙️ FFmpeg Kurulumu

Uygulama önce `C:\ffmpeg.exe` yolunu, ardından sistem `PATH` değişkenindeki `ffmpeg` executable'ını kontrol eder.

### Windows

```powershell
winget install Gyan.FFmpeg
```

Alternatif olarak FFmpeg'i indirip PATH'e ekleyebilirsiniz.

### macOS

```bash
brew install ffmpeg
```

### Debian / Ubuntu

```bash
sudo apt install ffmpeg
```

Kaynak kodunda FFmpeg bulunamadığında Windows'ta `winget`, macOS'ta `brew`, Linux'ta ise `apt` üzerinden otomatik kurulum denenmektedir. fileciteturn272file0

## ▶️ Kullanım

1. Uygulamayı başlatın.
2. Kayıt yapılacak ekranı veya desteklenen pencere seçimini belirleyin.
3. Çözünürlüğü seçin.
4. FPS değerini seçin.
5. Mikrofon ve sistem sesi seçeneklerini yapılandırın.
6. Kayıt düğmesine basın.
7. Kayıt süresini arayüzde takip edin.
8. Kaydı durdurduğunuzda video çıktı klasörüne kaydedilir.

Varsayılan kayıt dizini:

```text
Videos/
└── EliteScreenRecorder/
    └── Kayitlar/
```

Windows'ta uygulama gerçek `Videos` klasörünü Windows Shell API üzerinden bulmayı dener; klasör taşınmışsa veya bulunamazsa alternatif kullanıcı klasörlerini kullanır. fileciteturn272file0

## 🖥️ Ekran ve Pencere Algılama

Windows üzerinde uygulama `EnumDisplayMonitors` ile bağlı ekranları algılayabilir.

Ayrıca görünür ve başlığı bulunan pencereler `EnumWindows` üzerinden listelenebilir.

Bu sayede uygulama yalnızca sabit bir ekran boyutuna bağlı kalmak yerine mevcut masaüstü ortamını keşfedebilir. fileciteturn272file0

## 🎙️ Ses Kaydı

Uygulama mikrofon/ses cihazları için `sounddevice` kullanır.

Windows tarafında kayıt cihazlarının FFmpeg ile uyumlu olması için DirectShow cihaz adlarının kullanılması hedeflenmiştir.

Temel bağımlılık:

```text
sounddevice
```

Ses cihazı bulunamadığında uygulamanın video kaydını tamamen engellememesi için ses bileşeni `HAS_SOUNDDEVICE` kontrolüyle ele alınmaktadır. fileciteturn272file0

## 🔄 Çalışma Mimarisi

```text
┌──────────────────────────┐
│     CustomTkinter GUI    │
│                          │
│ Screen / Window / FPS    │
│ Resolution / Audio       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Recording Manager    │
│      Python / Thread     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│          FFmpeg          │
│   Video + Audio Capture  │
│       Encode / Mux       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  EliteScreenRecorder/    │
│        Kayitlar/         │
└──────────────────────────┘
```

## 📁 Proje Yapısı

```text
elite-screen-recorder/
├── Ekran Kayıt Programı.py
├── LICENSE
├── README.md
└── .gitignore
```

## 🧪 Bağımlılık Yönetimi

Uygulama başlangıçta gerekli Python modüllerini kontrol eder:

```text
customtkinter
sounddevice
Pillow
```

Eksik modül tespit edilirse Python'un mevcut interpreter'ı üzerinden `pip install` çalıştırmayı dener. Kurulum başarısız olursa kullanıcıya manuel kurulum komutu gösterilir. fileciteturn272file0

Bu davranış kullanıcı deneyimini kolaylaştırsa da kurumsal veya kontrollü ortamlarda otomatik paket kurulumunun güvenlik/paket yönetimi politikalarıyla değerlendirilmesi önerilir.

## 🛡️ Windows Yönetici Yetkisi

Kaynak kodunda Windows üzerinde yönetici yetkisi kontrolü bulunur. Uygulama administrator olarak çalışmıyorsa UAC üzerinden kendisini yeniden başlatmayı dener.

Bu davranış özellikle ekran yakalama, pencere erişimi veya sistem seviyesinde gereken diğer işlemlerde izin problemlerini azaltmayı amaçlar. fileciteturn272file0

## ⚠️ Teknik Notlar

Bu proje tek Python dosyası üzerinde geliştirilmiş bir masaüstü uygulamasıdır ve bazı işletim sistemi özellikleri platforma özgü API'lere bağlıdır.

Özellikle:

- 8K kayıt yüksek CPU/GPU, RAM ve disk I/O gerektirebilir.
- Yüksek FPS ve çözünürlüklerde performans kullanılan donanıma bağlıdır.
- FFmpeg'in doğru kurulması kayıt kalitesi ve codec desteği için kritiktir.
- Windows'a özel ekran/pencere ve DirectShow işlemleri Linux/macOS'ta aynı şekilde çalışmayabilir.
- Otomatik `pip`/FFmpeg kurulumu internet bağlantısı ve uygun sistem yetkileri gerektirebilir.
- Kaynak kodunda Windows için `C:\ffmpeg.exe` özel yolu öncelikli olarak kontrol edilir.

## 🔐 Güvenlik ve Gizlilik

Ekran kayıt uygulamaları masaüstündeki hassas bilgileri de kaydedebilir.

Kayıt almadan önce:

- Parola yöneticilerini ve hassas belgeleri kapatın veya gizleyin.
- Bildirimlerin görünmesini istemiyorsanız bildirimleri kapatın.
- Kaydedilen dosyaların erişim izinlerini kontrol edin.
- Kayıtları yalnızca yetkili olduğunuz içeriklerde kullanın.

Uygulama tarafından oluşturulan video dosyaları yerel disk üzerinde tutulur; README'de herhangi bir bulut yükleme özelliği tanımlanmamaktadır.

## 🛠️ Geliştirme Fikirleri

- Pause / Resume desteği
- WebM / MP4 / MKV çıktı seçimi
- Codec ve bitrate ayarlarının GUI'ye taşınması
- Sistem sesi için platformlar arası daha güçlü backend
- Kayıt öncesi disk alanı kontrolü
- Kayıt dosyası boyutu göstergesi
- Hotkey desteği
- Webcam overlay
- Mouse cursor highlight
- GPU encoding (`NVENC`, `AMF`, `QSV`) seçenekleri
- Profil kaydetme
- Çoklu monitör gelişmiş seçimleri
- Otomatik güncelleme sistemi
- PyInstaller ile dağıtılabilir paket oluşturma

## 📄 Lisans

Bu proje **Apache License 2.0** altında lisanslanmıştır.

Lisans metni için repository'deki [`LICENSE`](./LICENSE) dosyasına bakabilirsiniz.

## 👤 Geliştirici

**Ebubekir Bastama**

[GitHub profili](https://github.com/ebubekirbastama)

---

⭐ Projeyi faydalı bulduysanız repository'ye yıldız bırakabilirsiniz.
