const FALLBACK_INIT_DATA = 'query_id=AAHvA60xAgAAAO8DrTEiKsT7&user=%7B%22id%22%3A5128389615%2C%22first_name%22%3A%22Sanzhar%20%7C%20SKT%20CEO%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22swydk_dev%22%2C%22language_code%22%3A%22ru%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FAPs6KkcX_RZkiglsv5HWS_kXH4fcAk9YWVxHA6rpf4Mg82VDcsNBFE0G9Y4daf6J.svg%22%7D&auth_date=1753639189&signature=l9buVrlhgrBdv0SFEVD9E5RUjcJ0RgYGVxp5t2l5ANHWdDa_rYwQe7Y4UqTf0pRKIrv7qot9eU_gvObdV19HDA&hash=5f2484e13386554005e46607bafaeab6e71a4614f09ce89601d794f1316850a8';

export const getTelegramHeaders = () => ({
  'Content-Type': 'application/json',
  'InitData': window.Telegram?.WebApp?.initData || FALLBACK_INIT_DATA,
});

export default getTelegramHeaders;
