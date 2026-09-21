# Pointing gofishcr.com at the new site — for Tyler

Two records change in GoDaddy. Everything else stays exactly as it is.
Takes about five minutes. The website stays up the whole time.

## Where to go

GoDaddy → sign in → **My Products** → **Domains** → **gofishcr.com** → **DNS**
(the button may say *Manage DNS* or *Manage Zones*)

## Change 1 — the A record

Find the record that looks like this and **delete** it:

| Type | Name | Value |
|---|---|---|
| A | @ | 68.183.106.11 |

Then **add four new A records**, all with the name `@`, TTL 1 hour:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

Yes, four separate records, all named `@`. That is normal and correct.

## Change 2 — the www record

Find the record with Type **CNAME**, Name **www**.
Change its value to:

```
anthonyskoczylas.github.io
```

(If GoDaddy adds a dot on the end, leave it.)

## Please do not touch anything else

**Leave every MX record and every TXT record exactly as they are.**
Those run your Google email for gofishcr.com. If an MX record is deleted or
changed, email stops working — and the booking alerts from the website go with it.

Only the A record and the www CNAME change. Nothing else.

## When it is saved

Message Tony. He finishes the switch on our side within a minute, then the
secure padlock gets turned on once the certificate is issued, usually within
the hour.

The old address can take up to an hour to expire around the world, so some
people will see the old site and some the new one during that window. That is
expected and it sorts itself out.

## Keep the old hosting running for a few days

Do not cancel the current host yet. It is the safety net if anything needs
rolling back.
