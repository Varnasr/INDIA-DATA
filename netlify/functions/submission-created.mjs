// Netlify runs this for every verified form submission. For the support form
// it writes back to the sender with the UPI ID and sends PinPoint Ventures a
// copy. It needs RESEND_API_KEY and SUPPORT_FROM (an address on a domain
// verified with Resend) in the site's environment; without them it does
// nothing, and the submission still waits in the Netlify dashboard. Other
// forms (share-data) are left alone.
const TEAM = 'info@pinpointventures.in';
const UPI = 'impactmojo@ibl';

export default async (req) => {
  const { payload } = await req.json();
  if (!payload || payload.form_name !== 'support') return new Response('ignored');
  const key = process.env.RESEND_API_KEY, from = process.env.SUPPORT_FROM;
  if (!key || !from) return new Response('no mail service configured');
  const d = payload.data || {}, name = String(d.name || '').slice(0, 120), email = String(d.email || '').trim();
  const send = (body) => fetch('https://api.resend.com/emails', {
    method: 'POST', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const out = [];
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    out.push(send({ from, to: email, reply_to: TEAM, subject: 'Thank you for supporting Off the Roll',
      text: `Dear ${name || 'reader'},\n\nThank you for offering to support Off the Roll. If you would like to contribute, any UPI app can pay to this UPI ID:\n\n${UPI}\n\nYou choose the amount in your app. If you offered other help, we will write to you about it separately.\n\nSupport does not buy influence over what the site publishes. Every figure still comes from a source.\n\nOff the Roll, PinPoint Ventures\n${TEAM}\n` }));
  }
  out.push(send({ from, to: TEAM, reply_to: /@/.test(email) ? email : undefined, subject: `Support form: ${name || 'no name'} (${d.how || 'not said'})`,
    text: `Name: ${name}\nEmail: ${email}\nHow: ${d.how || ''}\nMessage:\n${d.message || ''}\n` }));
  await Promise.allSettled(out);
  return new Response('ok');
};
