# Поисковые шаблоны после переноса

Проверяй совпадения по контексту. Не удаляй легитимный текст только потому, что
в нём встречается слово `motor`.

```text
SOURCE_DOMAIN
public.bundle
bundle
lpmotor
motor
editor
runtime
vendor
src=""
srcset=""
url()
http://
iframe
data:image
serviceWorker
sourceMappingURL
```

Дополнительно проверь:

- абсолютные ссылки на технический домен;
- внешние CSS/JS конструктора;
- скрытые desktop/mobile копии;
- повторное подключение аналитики;
- повторное подключение обработчика форм;
- изображения без width/height;
- LCP-изображение с lazy loading;
- несколько `fetchpriority="high"`;
- `transition: all`;
- анимации `top/left/width/height`;
- пустые media queries;
- неиспользуемые шрифтовые начертания.
