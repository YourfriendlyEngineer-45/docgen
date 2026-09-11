-- custom.lua — the file a non-programmer edits.
--
-- Called once per invoice. `data` contains:
--   data.subtotal            (number)
--   data.customer.country    (string)
--   data.tier                (string)
--   data.years_customer      (number)
--   data.items               (array of {sku, description, quantity, unit_price, line_total})
--
-- Return a flat table. Python picks up every key/value pair.

function compute(data)
  local subtotal = data.subtotal or 0

  local country = data.customer.country or ""
  local is_eu   = (country == "DE" or country == "FR" or country == "IT"
                or country == "ES" or country == "NL" or country == "IE")
  local is_uk   = (country == "GB")
  local is_loyal     = (data.years_customer or 0) >= 3
  local is_vip       = (data.tier == "vip")
  local is_over_1000 = subtotal >= 1000

  -- discount policy
  local discount = 0
  if is_loyal     then discount = discount + 0.05 end
  if is_vip       then discount = discount + 0.10 end
  if is_over_1000 then discount = discount + 0.05 end
  if discount > 0.15 then discount = 0.15 end

  local discount_amount = subtotal * discount
  local after_discount  = subtotal - discount_amount

  -- VAT policy
  local vat_rate = 0
  if is_uk or is_eu then vat_rate = 0.20 end

  local vat_amount = after_discount * vat_rate
  local total      = after_discount + vat_amount

  local function r2(x) return math.floor(x * 100 + 0.5) / 100 end

  return {
    discount_rate   = r2(discount),
    discount_amount = r2(discount_amount),
    vat_rate        = r2(vat_rate),
    vat_amount      = r2(vat_amount),
    total           = r2(total),
  }
end
