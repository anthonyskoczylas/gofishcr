# Answers for Tyler

## 1. Bookings — how they work on a static site

You're right that GitHub Pages only serves files. The forms post to a small
service of our own:

- **Endpoint:** `https://gofish-mail.vercel.app/api/request` (serverless function, Vercel)
- **Delivery:** Resend
- **Two emails per request:** a confirmation to the guest (photo of the boat or
  tour, what they asked for, what happens next) and an alert to
  **gofishcr@gmail.com** with everything needed to reply. Hitting reply on the
  alert goes straight to the guest.
- **Only our own site can post to it** (origin allow-list), and only photo/link
  URLs on gofishcr.com or the preview host are accepted, so nothing can be
  injected into the emails.
- **If the service is ever unreachable**, the form falls back to opening the
  guest's own mail app with the whole request pre-filled. A booking is never
  silently lost.

**Tested end to end just now, on the live preview, before cutover:**

```
POST https://gofish-mail.vercel.app/api/request  ->  HTTP 200 {"ok":true}
Alert delivered to gofishcr@gmail.com
Guest confirmation delivered
Zero JavaScript errors
```

It is in your inbox with the name **"TEST BOOKING - please ignore"**. Take a
look and tell me if you want anything worded differently. Happy to run more
with you watching.

## 2. Repo ownership

Completely reasonable. Two options, Tony's call:

- **Add you as admins** on the existing repository, or
- **Transfer it to a Go Fish organisation** you own, with Tony kept as a
  collaborator so he can keep maintaining it.

Either works and neither causes downtime. Send me the GitHub usernames or the
org name and we'll sort it.

## 3. Pages setup and the CNAME file

Not set yet, deliberately. The moment a custom domain is set on the repo, the
current preview address starts redirecting to gofishcr.com, which today is
still the old site. That would take your preview away before you've reviewed it.

**The plan avoids any 404 window:** the second you save the DNS change, message
us. Setting the custom domain and committing the CNAME file takes under a
minute. DNS takes up to an hour to reach everyone. So GitHub is ready and
waiting long before the first visitor is routed there.

## 4. Preview link

Live now, this is the finished site:

**https://anthonyskoczylas.github.io/gofishcr/**

Worth a look at: the trip planner (`/book.html`) which now plans a whole week,
any boat page for the booking panel and the map pin, and the same pages on a
phone.

## 5. HTTPS

Yes. Enforce HTTPS goes on as soon as GitHub issues the certificate, usually
within the hour after DNS resolves. The repo already has enforcement switched
on, so it applies the moment the certificate exists. I'll confirm when it's green.

## 6. The _github-pages-challenge TXT record

Thanks for offering to add it, and for flagging that you won't touch the
existing MX or TXT records. That's exactly right.

That value is generated per account and can only be created in the browser, so
Tony will produce it from his GitHub settings and send it straight over. It
looks like:

```
Type:  TXT
Name:  _github-pages-challenge-anthonyskoczylas
Value: (a one-off string GitHub generates)
```

Worth knowing: this verification is **optional**. It stops anyone else claiming
gofishcr.com on GitHub later. The site works with or without it, so it doesn't
hold up the cutover.
