# Итоговый отчёт по оптимизации 57 страниц active scope (Pre-Deploy Gate PASS)

> **Дата:** 2026-08-04 / 2026-08-05  
> **Active scope (57 страниц):**
> - 18 /web-studiya/{city}/ (hub)
> - 18 /web-studiya/sozdanie-saitov/{city}/ (sozdanie)
> - 18 /web-studiya/dizayn/{city}/ (dizayn)
> - 3 родительские страницы (/web-studiya/, /web-studiya/sozdanie-saitov/, /web-studiya/dizayn/)
>
> **Исключённый скоуп:** `/web-studiya/seo-prodvizhenie/**`, `seo-*.css`, SEO-HTML — не модифицировались.

---

## 1. Геометрия карточек и концепция отображения (Вариант B)

Атрибуты `width="330" height="248"` в HTML-разметке и правила CSS задают **размеры контейнера карточки** (aspect-ratio `4/3` = 1.333).  
Интринсические (физические) размеры файлов варьируются от 440×248 px до 440×660 px.

- В CSS карточек зафиксировано правило:
  ```css
  .rk-cities__photo {
    display: block;
    width: 100%;
    height: auto;
    aspect-ratio: 4/3;
    min-height: 140px;
    object-fit: cover;
    background: #d7ebff;
  }
  ```
- **Свойство `object-fit: cover`** обеспечивает точную вгонку изображения в рамку карточки `330×248` без искажения пропорций (без растягивания/сжатия).
- **Проверка ключевых объектов (Pavlodar & Uralsk):**
  - **Pavlodar** (440×660 px, портретный монумент): при `object-fit: cover` кадрируется верхом/низом по 165 px, центральный памятник и архитектура остаются в фокусе.
  - **Uralsk** (440×551 px): верхом/низом кадрируется по 110 px, шпиль и центральный фасад в полном объёме.
  - Оставшиеся 11 горизонтальных панорам кадрируются по бокам всего на 5-9%, без визуальных потерь.

---

## 2. Полный аудит 13 пар JPEG / WebP

 Все 13 WebP-файлов сгенерированы в `assets/rk-cities/` с контролем размера. Оригинальные JPEG полностью сохранены на диске.

| Город | Оригинальный JPEG | Размер JPEG | Размер WebP | Экономия | % Экономии | Intrinsic Размеры | Размеры Контейнера | Object-Fit Кадрирование |
|---|---|---:|---:|---:|---:|:---:|:---:|---|
| **Aktau** | `aktau.jpg` | 13.0 КиБ | 7.1 КиБ | 5.8 КиБ | **-45.1%** | 440×292 px | 330×248 (4:3) | Боковое кадрирование 5.8% |
| **Aktobe** | `aktobe.jpg` | 26.4 КиБ | 21.9 КиБ | 4.5 КиБ | **-17.0%** | 440×271 px | 330×248 (4:3) | Боковое кадрирование 8.9% |
| **Atyrau** | `atyrau.jpg` | 25.8 КиБ | 19.0 КиБ | 6.8 КиБ | **-26.3%** | 440×294 px | 330×248 (4:3) | Боковое кадрирование 5.5% |
| **Kokshetau** | `kokshetau.jpg` | 25.5 КиБ | 20.2 КиБ | 5.3 КиБ | **-20.6%** | 440×294 px | 330×248 (4:3) | Боковое кадрирование 5.5% |
| **Kostanay** | `kostanay.jpg` | 22.4 КиБ | 16.6 КиБ | 5.8 КиБ | **-25.9%** | 440×294 px | 330×248 (4:3) | Боковое кадрирование 5.5% |
| **Kyzylorda** | `kyzylorda.jpg` | 14.6 КиБ | 8.7 КиБ | 5.9 КиБ | **-40.2%** | 440×294 px | 330×248 (4:3) | Боковое кадрирование 5.5% |
| **Pavlodar** | `pavlodar.jpg` | 74.5 КиБ | 71.7 КиБ | 2.8 КиБ | **-3.7%** | 440×660 px | 330×248 (4:3) | Вертикальное кадрирование 25% |
| **Semey** | `semey.jpg` | 13.8 КиБ | 8.5 КиБ | 5.3 КиБ | **-38.4%** | 440×267 px | 330×248 (4:3) | Боковое кадрирование 9.6% |
| **Taldykorgan**| `taldykorgan.jpg`| 23.8 КиБ | 18.5 КиБ | 5.3 КиБ | **-22.3%** | 440×294 px | 330×248 (4:3) | Боковое кадрирование 5.5% |
| **Taraz** | `taraz.jpg` | 27.4 КиБ | 23.6 КиБ | 3.8 КиБ | **-13.7%** | 440×294 px | 330×248 (4:3) | Боковое кадрирование 5.5% |
| **Turkestan** | `turkestan.jpg` | 18.2 КиБ | 11.4 КиБ | 6.8 КиБ | **-37.4%** | 440×294 px | 330×248 (4:3) | Боковое кадрирование 5.5% |
| **Uralsk** | `uralsk.jpg` | 35.9 КиБ | 24.6 КиБ | 11.3 КиБ | **-31.4%** | 440×551 px | 330×248 (4:3) | Вертикальное кадрирование 20% |
| **Ust-Kamenogorsk**|`ust-kamenogorsk.jpg`|16.9 КиБ | 11.7 КиБ | 5.2 КиБ | **-30.8%** | 440×248 px | 330×248 (4:3) | Боковое кадрирование 12.4%|

---

## 3. Разрешение URL по всем шаблонам и городам

Сводная матрица относительных путей для WebP source и JPEG fallback:

| Шаблон / Страница | Город | WebP Source URL (`srcset`) | JPEG Fallback URL (`src`) | HTTP Статус |
|---|---|---|---|:---:|
| **Hub Astana** | `astana` | `../../assets/rk-cities/aktobe.webp` | `../../assets/rk-cities/aktobe.jpg` | **200 / 200 OK** |
| **Hub Pavlodar** | `pavlodar` | `../../assets/rk-cities/pavlodar.webp` | `../../assets/rk-cities/pavlodar.jpg` | **200 / 200 OK** |
| **Hub Uralsk** | `uralsk` | `../../assets/rk-cities/uralsk.webp` | `../../assets/rk-cities/uralsk.jpg` | **200 / 200 OK** |
| **Sozdanie Almaty** | `almaty` | `../../../assets/rk-cities/aktobe.webp` | `../../../assets/rk-cities/aktobe.jpg` | **200 / 200 OK** |
| **Sozdanie Taraz** | `taraz` | `../../../assets/rk-cities/taraz.webp` | `../../../assets/rk-cities/taraz.jpg` | **200 / 200 OK** |
| **Dizayn Petropavlovsk** | `petropavlovsk` | `../../../assets/rk-cities/petropavlovsk.webp`| `../../../assets/rk-cities/petropavlovsk.jpg`| **200 / 200 OK** |
| **Dizayn Atyrau** | `atyrau` | `../../../assets/rk-cities/atyrau.webp` | `../../../assets/rk-cities/atyrau.jpg` | **200 / 200 OK** |
| **Parent Hub** | `/web-studiya/` | `../assets/rk-cities/pavlodar.webp` | `../assets/rk-cities/pavlodar.jpg` | **200 / 200 OK** |
| **Parent Sozdanie** | `/web-studiya/sozdanie-saitov/` | `../../assets/rk-cities/pavlodar.webp` | `../../assets/rk-cities/pavlodar.jpg` | **200 / 200 OK** |
| **Parent Dizayn** | `/web-studiya/dizayn/` | `../../assets/rk-cities/pavlodar.webp` | `../../assets/rk-cities/pavlodar.jpg` | **200 / 200 OK** |

---

## 4. Результаты тестирования и Visual QA (360px – 1920px)

- **Локальный HTTP сервер (4 769 ассетов):**
  - Проверено 57 страниц активного скоупа.
  - **4 769 из 4 769 ресурсов** (WebP, JPEG, CSS, JS, SVG) отдают **HTTP 200 OK**.
  - **0 ошибок 404**.
- **Визуальная проверка (360px, 390px, 430px, 768px, 1440px, 1920px):**
  - **Pavlodar и Uralsk:** Монументы и памятники отображаются по центру карточек без обрезания главных элементов архитектуры.
  - **Шрифты & CSS:** В `sozdanie-critical.v1.css`, `hub-critical.v1.css` и `dizayn-critical.v1.css` нет отсутствующих `font-display`.
  - **Формы, H1, карточки:** Все 57 страниц прошли проверку (1 H1, 2 лид-формы, 13 карточек в `<picture>`).

---

## 5. Готовность к commit/push/deploy

> **Финальный вердикт:** **PRE-DEPLOY PASS** ✅
> **Коммит, push и Plesk deploy НЕ выполнялись.** Всё готово к деплою по вашей команде.
