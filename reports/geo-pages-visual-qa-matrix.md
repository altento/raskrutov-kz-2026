# Visual QA matrix — geo representatives

> Дата: 2026-08-04 · local `http://127.0.0.1:8767` из `site_mirror`  
> Ширины: 360, 390, 430, 768, 1024, 1440, 1920 px  
> Commit / push / deploy: **нет**

## Verdict

- **CSS-extract:** COMPLETED
- **Visual QA:** **PASS** (mobile H1 **FIXED**)
- **PSI:** POST-DEPLOY (не измерялся)

## Mobile H1 fix (2026-08-04)

**Причина:** Mottor rule в `hub-deferred` / `seo-deferred` (+ popup-menu):

```css
div.blk_text .blk-data.blk-data--pc{display:block}
div.blk_text .blk-data.blk-data--mobile370{display:none}
@media(max-width:500px){
  div.blk_text .blk-data.blk-data--pc{display:none}
  div.blk_text .blk-data.blk-data--mobile370{display:block}
}
```

Гео-`<h1 class="blk-data--pc">` прятался; показывался дубль `.blk-data--mobile370.heading--rank-1` («Веб-студия полного цикла…»).

**Фикс:** scoped inline `<style data-rk-mobile-h1-fix="1">` только на **18 hub + 18 seo city** pages — блок `b-aa35398c497a44568f98430c09d8d76c`: на ≤500px H1 `display:block`, Mottor-дубль `display:none`. CSS-extract файлы **не** трогали. sozdanie / dizayn / parents — без изменений.

Скрипт: `_fix_mobile_h1_geo.py`.

## Pages

### `/web-studiya/astana/` (hub)

| Width | H1 | Mottor duplicate | Crit CSS |
|---:|---|---|---|
| 360 / 390 / 430 | «Веб-студия в Астане» **visible** | hidden | hub-critical + popup-menu |
| 768–1920 | city H1 visible | n/a (pc) | OK |

### `/web-studiya/sozdanie-saitov/almaty/` (sozdanie)

| Width | Status |
|---:|---|
| 360–1920 | PASS (не затронут фиксом) |

### `/web-studiya/seo-prodvizhenie/shymkent/` (seo)

| Width | H1 | Mottor duplicate |
|---:|---|---|
| 360 / 390 / 430 | «SEO-продвижение сайтов в Шымкенте» **visible** | hidden |
| 1440 | city H1 visible | mobile370 `display:none` (desk) |

### `/web-studiya/dizayn/petropavlovsk/` (dizayn)

| Width | Status |
|---:|---|
| 360–1920 | PASS (не затронут фиксом) |

## Checks covered

- hero / first screen after H1 fix (Astana @390, Shymkent @360 screenshots)
- CTA / mockups / menu / forms — без регрессий на проверенных экранах
- FOUC: critical CSS на месте; override только display H1/дубля
- PSI / formal CLS — POST-DEPLOY

## Warnings / remaining

1. ~~Mobile H1 hub/seo~~ → **FIXED**
2. **PSI scores** — только после деплоя
3. Absolute `CANVAS` widget scrollWidth — без изменений
