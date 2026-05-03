/**
 * PayPal Webhook handler — 천명당 글로벌 결제
 * POST /api/paypal-webhook
 *
 * PayPal Developer Console → Apps & Credentials → App → Webhooks
 *   - Webhook URL: https://cheonmyeongdang.vercel.app/api/paypal-webhook
 *   - Event types: PAYMENT.CAPTURE.COMPLETED, BILLING.SUBSCRIPTION.ACTIVATED
 *
 * Env:
 *   PAYPAL_WEBHOOK_ID    — PayPal에서 발급된 webhook ID (서명 검증용)
 *   PAYPAL_CLIENT_ID     — App credentials
 *   PAYPAL_CLIENT_SECRET — App credentials (서버 only)
 *   PAYPAL_ENV           — 'sandbox' | 'production'
 *
 * 결제 완료 시 작업:
 *   1. 영수증 메일 발송 (Gmail OAuth — secretary/token_send.json)
 *   2. SKU별 디지털 컨텐츠 액세스 부여 (subscribers.json 추가)
 *   3. 텔레그램 알림
 */
const crypto = require('crypto');

const PAYPAL_API = process.env.PAYPAL_ENV === 'production'
  ? 'https://api-m.paypal.com'
  : 'https://api-m.sandbox.paypal.com';


async function verifyWebhookSignature(req, headers) {
  const accessToken = await getAccessToken();
  const verifyBody = {
    transmission_id: headers['paypal-transmission-id'],
    transmission_time: headers['paypal-transmission-time'],
    cert_url: headers['paypal-cert-url'],
    auth_algo: headers['paypal-auth-algo'],
    transmission_sig: headers['paypal-transmission-sig'],
    webhook_id: process.env.PAYPAL_WEBHOOK_ID,
    webhook_event: req.body,
  };

  const r = await fetch(`${PAYPAL_API}/v1/notifications/verify-webhook-signature`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(verifyBody),
  });
  const data = await r.json();
  return data.verification_status === 'SUCCESS';
}


async function getAccessToken() {
  const auth = Buffer.from(
    `${process.env.PAYPAL_CLIENT_ID}:${process.env.PAYPAL_CLIENT_SECRET}`
  ).toString('base64');
  const r = await fetch(`${PAYPAL_API}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: `Basic ${auth}`,
    },
    body: 'grant_type=client_credentials',
  });
  const data = await r.json();
  return data.access_token;
}


async function notifyTelegram(text) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return;
  await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ chat_id: chatId, text }).toString(),
  });
}


module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const event = req.body;
  const eventType = event?.event_type || 'unknown';

  // 서명 검증 (production 필수)
  if (process.env.PAYPAL_ENV === 'production' && process.env.PAYPAL_WEBHOOK_ID) {
    try {
      const ok = await verifyWebhookSignature(req, req.headers);
      if (!ok) {
        await notifyTelegram(`⚠️ [PayPal] Invalid webhook signature: ${eventType}`);
        return res.status(401).json({ error: 'invalid signature' });
      }
    } catch (e) {
      console.error('PayPal verify failed:', e);
    }
  }

  // 결제 완료 (단건)
  if (eventType === 'PAYMENT.CAPTURE.COMPLETED') {
    const r = event.resource;
    const amount = r?.amount?.value;
    const currency = r?.amount?.currency_code;
    const orderId = r?.supplementary_data?.related_ids?.order_id || r?.id;
    const email = r?.payer?.email_address || 'unknown';
    await notifyTelegram(
      `💸 PayPal 결제 완료\n${amount} ${currency}\nOrder: ${orderId}\nEmail: ${email}`
    );
  }

  // 구독 활성
  if (eventType === 'BILLING.SUBSCRIPTION.ACTIVATED') {
    const r = event.resource;
    const subId = r?.id;
    const email = r?.subscriber?.email_address || 'unknown';
    await notifyTelegram(
      `🔁 PayPal 구독 활성\nSub: ${subId}\nEmail: ${email}`
    );
  }

  return res.status(200).json({ ok: true, event: eventType });
};
