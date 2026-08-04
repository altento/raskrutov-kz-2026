# Контракт формы — памятка

## Базовый пример для проекта с глобальным обработчиком

```html
<form
  class="lead-form"
  data-lead-form
  data-form-name="Страница — назначение формы"
  novalidate
>
  <div class="field">
    <label for="lead-name">Ваше имя</label>
    <input
      id="lead-name"
      name="name"
      type="text"
      autocomplete="name"
    >
  </div>

  <div class="field">
    <label for="lead-phone">Телефон</label>
    <input
      id="lead-phone"
      name="phone"
      type="tel"
      inputmode="tel"
      autocomplete="tel"
      required
      aria-describedby="lead-phone-error"
    >
    <span id="lead-phone-error" data-field-error="phone"></span>
  </div>

  <input
    class="lead-form-honeypot"
    type="text"
    name="website"
    autocomplete="off"
    tabindex="-1"
    aria-hidden="true"
  >

  <label class="consent">
    <input name="consent" type="checkbox" value="accepted" required>
    <span>
      Согласен на обработку персональных данных и ознакомлен с
      <a href="/politika-konfidencialnosti/" target="_blank" rel="noopener">
        политикой конфиденциальности
      </a>
    </span>
  </label>

  <button type="submit">Отправить</button>
  <div data-form-status aria-live="polite" aria-atomic="true"></div>
</form>
```

## Важно

- Уникализируй `id` внутри каждой формы.
- `data-form-name` должно описывать страницу и расположение.
- Не копируй этот пример механически, если backend использует другой контракт.
- Не добавляй отдельный JS-submit при наличии общего обработчика.
- Не прописывай скрытые UTM/page_url повторно, если общий модуль добавляет их сам.
