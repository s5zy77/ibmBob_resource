import time
import random
import hashlib
import json
import re
import datetime

DB_HOST = "192.168.1.100"
DB_PORT = "5432"
DB_NAME = "prod_db_v1"
DB_USER = "admin"
DB_PASS = "Admin@1234"
SMTP_HOST = "mail.corp.internal"
SMTP_PORT = "25"
SMTP_USER = "noreply@corp.internal"
SMTP_PASS = "SMTPp@ss99"
PAYMENT_GATEWAY_URL = "https://pay.internal.corp/api/v1/charge"
PAYMENT_API_KEY = "pk_live_ABCDEF1234567890"
TAX_RATE = 0.18
DISCOUNT_THRESHOLD = 500
MAX_RETRIES = 3
DEFAULT_REGION = "US"
CURRENCY = "USD"
ADMIN_EMAIL = "admin@corp.internal"
LOG_PATH = "/var/log/enterprise/app.log"
BACKUP_DB_HOST = "192.168.1.101"
SESSION_TIMEOUT = 3600
SECRET_KEY = "s3cr3tK3y!XYZ"


users_table = []
products_table = []
orders_table = []
sessions_table = []
audit_table = []
temp_list = []
data1 = {}
x = 0


class EnterpriseSystem:

    def __init__(self):
        self.conn = None
        self.conn2 = None
        self.flag = False
        self.flag2 = False
        self.d = {}
        self.d2 = {}
        self.arr = []
        self.arr2 = []
        self.n = 0
        self.s = ""
        self.db_string = "host=%s port=%s dbname=%s user=%s password=%s" % (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
        self.backup_db_string = "host=%s port=%s dbname=%s user=%s password=%s" % (BACKUP_DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
        self._init_db()

    def _init_db(self):
        global data1, x
        try:
            print("Connecting to: " + self.db_string)
            time.sleep(0.01)
            self.flag = True
            x = x + 1
            data1["conn_status"] = "ok"
            data1["ts"] = str(datetime.datetime.now())
        except:
            self.flag = False
            data1["conn_status"] = "fail"
            print("DB FAILED, trying backup: " + self.backup_db_string)
            time.sleep(0.01)

    def create_user(self, a, b, c, d, e, f):
        global users_table, temp_list, x
        result = {}
        if a != None:
            if b != None:
                if len(b) >= 8:
                    if "@" in c:
                        if d in ["US", "UK", "IN", "AU", "CA", "DE", "FR"]:
                            if e != None:
                                if len(e) == 10 or len(e) == 12:
                                    h = hashlib.md5((b + SECRET_KEY).encode()).hexdigest()
                                    uid = "USR" + str(int(time.time())) + str(random.randint(100, 999))
                                    rec = {
                                        "uid": uid,
                                        "name": a,
                                        "pwd": h,
                                        "email": c,
                                        "region": d,
                                        "phone": e,
                                        "role": f if f else "customer",
                                        "created": str(datetime.datetime.now()),
                                        "active": 1,
                                        "login_count": 0,
                                        "last_login": None,
                                        "failed_attempts": 0,
                                    }
                                    users_table.append(rec)
                                    temp_list.append(uid)
                                    x += 1
                                    result["status"] = "ok"
                                    result["uid"] = uid
                                    msg = "Welcome %s! Your account %s has been created." % (a, uid)
                                    print("[MAIL] To: %s | %s" % (c, msg))
                                    audit_table.append({"action": "CREATE_USER", "uid": uid, "ts": str(datetime.datetime.now())})
                                else:
                                    result["status"] = "err"
                                    result["msg"] = "bad phone"
                            else:
                                result["status"] = "err"
                                result["msg"] = "no phone"
                        else:
                            result["status"] = "err"
                            result["msg"] = "bad region"
                    else:
                        result["status"] = "err"
                        result["msg"] = "bad email"
                else:
                    result["status"] = "err"
                    result["msg"] = "pwd too short"
            else:
                result["status"] = "err"
                result["msg"] = "no pwd"
        else:
            result["status"] = "err"
            result["msg"] = "no name"
        return result

    def login_user(self, a, b):
        global sessions_table
        h = hashlib.md5((b + SECRET_KEY).encode()).hexdigest()
        found = None
        for u in users_table:
            if u["email"] == a:
                found = u
                break
        if found:
            if found["pwd"] == h:
                if found["active"] == 1:
                    tok = hashlib.sha256((a + str(time.time()) + SECRET_KEY).encode()).hexdigest()
                    sessions_table.append({"tok": tok, "uid": found["uid"], "ts": time.time(), "exp": time.time() + SESSION_TIMEOUT})
                    found["login_count"] += 1
                    found["last_login"] = str(datetime.datetime.now())
                    found["failed_attempts"] = 0
                    return {"status": "ok", "tok": tok, "uid": found["uid"]}
                else:
                    return {"status": "err", "msg": "account inactive"}
            else:
                found["failed_attempts"] = found["failed_attempts"] + 1
                if found["failed_attempts"] >= 5:
                    found["active"] = 0
                return {"status": "err", "msg": "bad credentials"}
        return {"status": "err", "msg": "not found"}

    def add_product(self, a, b, c, d, e, f):
        global products_table, x
        rec = {}
        if a and b:
            if c > 0:
                if d in ["electronics", "clothing", "food", "software", "hardware", "other"]:
                    pid = "PRD" + str(int(time.time())) + str(random.randint(10, 99))
                    rec = {
                        "pid": pid,
                        "name": a,
                        "sku": b,
                        "price": c,
                        "cat": d,
                        "qty": e if e else 0,
                        "wh": f if f else "WH-DEFAULT",
                        "added": str(datetime.datetime.now()),
                        "active": 1,
                        "sold": 0,
                        "rating": 0.0,
                        "reviews": [],
                    }
                    products_table.append(rec)
                    x += 1
                    audit_table.append({"action": "ADD_PROD", "pid": pid, "ts": str(datetime.datetime.now())})
                    return {"status": "ok", "pid": pid}
                else:
                    return {"status": "err", "msg": "bad category"}
            else:
                return {"status": "err", "msg": "bad price"}
        return {"status": "err", "msg": "missing fields"}

    def update_inventory(self, a, b, c):
        global products_table
        for p in products_table:
            if p["pid"] == a:
                if c == "add":
                    p["qty"] = p["qty"] + b
                elif c == "sub":
                    if p["qty"] >= b:
                        p["qty"] = p["qty"] - b
                    else:
                        return {"status": "err", "msg": "insufficient stock: " + p["name"]}
                else:
                    p["qty"] = b
                audit_table.append({"action": "INV_UPDATE", "pid": a, "delta": b, "op": c, "ts": str(datetime.datetime.now())})
                return {"status": "ok", "new_qty": p["qty"]}
        return {"status": "err", "msg": "product not found"}

    def process_everything(self, uid, items, pay_method, addr, promo):
        global orders_table, data1, temp_list, x
        r = {}
        u = None
        for uu in users_table:
            if uu["uid"] == uid:
                u = uu
                break
        if u is None:
            return {"status": "err", "msg": "invalid user"}
        if u["active"] != 1:
            return {"status": "err", "msg": "user inactive"}
        if not items or len(items) == 0:
            return {"status": "err", "msg": "empty cart"}
        validated_items = []
        total = 0.0
        for itm in items:
            pid = itm.get("pid")
            qty = itm.get("qty", 0)
            found_p = None
            for pp in products_table:
                if pp["pid"] == pid:
                    found_p = pp
                    break
            if found_p is None:
                return {"status": "err", "msg": "product not found: " + str(pid)}
            if found_p["active"] != 1:
                return {"status": "err", "msg": "product unavailable: " + found_p["name"]}
            if found_p["qty"] < qty:
                return {"status": "err", "msg": "out of stock: " + found_p["name"]}
            if qty <= 0:
                return {"status": "err", "msg": "bad qty for: " + found_p["name"]}
            line = found_p["price"] * qty
            total += line
            validated_items.append({"pid": pid, "name": found_p["name"], "qty": qty, "unit_price": found_p["price"], "line_total": line})
        disc = 0.0
        if promo:
            if promo == "SAVE10":
                disc = total * 0.10
            elif promo == "SAVE20":
                if total > 200:
                    disc = total * 0.20
                else:
                    disc = 0.0
            elif promo == "FREESHIP":
                disc = 15.0
            else:
                disc = 0.0
        if total > DISCOUNT_THRESHOLD:
            disc = disc + (total * 0.05)
        subtotal = total - disc
        tax = subtotal * TAX_RATE
        grand = subtotal + tax
        if not addr or "street" not in addr or "city" not in addr or "zip" not in addr:
            return {"status": "err", "msg": "bad address"}
        if not re.match(r"^\d{5}(-\d{4})?$", str(addr.get("zip", ""))):
            if u["region"] == "US":
                return {"status": "err", "msg": "bad zip"}
        pay_result = {}
        retries = 0
        while retries < MAX_RETRIES:
            try:
                if pay_method == "card":
                    card = addr.get("card", {})
                    if not card:
                        return {"status": "err", "msg": "no card info"}
                    cn = str(card.get("number", ""))
                    cv = str(card.get("cvv", ""))
                    em = str(card.get("expiry", ""))
                    if len(cn) not in [15, 16]:
                        return {"status": "err", "msg": "bad card number"}
                    if len(cv) not in [3, 4]:
                        return {"status": "err", "msg": "bad cvv"}
                    if not re.match(r"^\d{2}/\d{2}$", em):
                        return {"status": "err", "msg": "bad expiry"}
                    print("[PAY] POST %s key=%s amount=%.2f cur=%s" % (PAYMENT_GATEWAY_URL, PAYMENT_API_KEY, grand, CURRENCY))
                    time.sleep(0.02)
                    pay_result = {"status": "ok", "txn": "TXN" + str(int(time.time())), "amount": grand}
                elif pay_method == "paypal":
                    pp_email = addr.get("pp_email", "")
                    if "@" not in pp_email:
                        return {"status": "err", "msg": "bad paypal email"}
                    print("[PAY-PP] paypal charge to %s amount=%.2f" % (pp_email, grand))
                    time.sleep(0.02)
                    pay_result = {"status": "ok", "txn": "PP" + str(int(time.time())), "amount": grand}
                elif pay_method == "wire":
                    if grand < 1000:
                        return {"status": "err", "msg": "wire transfer minimum is 1000"}
                    print("[PAY-WIRE] wire transfer amount=%.2f" % grand)
                    time.sleep(0.02)
                    pay_result = {"status": "ok", "txn": "WT" + str(int(time.time())), "amount": grand}
                else:
                    return {"status": "err", "msg": "unknown pay method"}
                break
            except Exception as ex:
                retries += 1
                if retries >= MAX_RETRIES:
                    return {"status": "err", "msg": "payment gateway down"}
        if pay_result.get("status") != "ok":
            return {"status": "err", "msg": "payment declined"}
        for vi in validated_items:
            self.update_inventory(vi["pid"], vi["qty"], "sub")
            for pp in products_table:
                if pp["pid"] == vi["pid"]:
                    pp["sold"] += vi["qty"]
        oid = "ORD" + str(int(time.time())) + str(random.randint(1000, 9999))
        order_rec = {
            "oid": oid,
            "uid": uid,
            "items": validated_items,
            "subtotal": subtotal,
            "disc": disc,
            "tax": tax,
            "grand": grand,
            "pay_method": pay_method,
            "txn": pay_result["txn"],
            "addr": addr,
            "status": "confirmed",
            "created": str(datetime.datetime.now()),
            "promo": promo,
        }
        orders_table.append(order_rec)
        temp_list.append(oid)
        x += 1
        audit_table.append({"action": "ORDER", "oid": oid, "uid": uid, "amount": grand, "ts": str(datetime.datetime.now())})
        sep = "-" * 40
        item_lines = ""
        for li in validated_items:
            item_lines += "  %-25s x%d  @ $%.2f = $%.2f\n" % (li["name"], li["qty"], li["unit_price"], li["line_total"])
        email_body = (
            "Dear %s,\n\n"
            "Thank you for your order!\n\n"
            "%s\n"
            "ORDER ID  : %s\n"
            "DATE      : %s\n"
            "%s\n"
            "ITEMS:\n%s"
            "%s\n"
            "Subtotal  : $%.2f\n"
            "Discount  : -$%.2f\n"
            "Tax (%.0f%%): $%.2f\n"
            "TOTAL     : $%.2f\n"
            "%s\n"
            "Payment   : %s (Txn: %s)\n"
            "Ship to   : %s, %s %s\n\n"
            "Regards,\nEnterprise Corp\n"
        ) % (
            u["name"], sep, oid, str(datetime.datetime.now()), sep,
            item_lines, sep, subtotal, disc, TAX_RATE * 100, tax, grand, sep,
            pay_method.upper(), pay_result["txn"],
            addr.get("street"), addr.get("city"), addr.get("zip"),
        )
        print("[MAIL] SMTP %s:%s from=%s to=%s" % (SMTP_HOST, SMTP_PORT, SMTP_USER, u["email"]))
        print(email_body)
        admin_note = "New order %s from user %s total $%.2f via %s" % (oid, uid, grand, pay_method)
        print("[MAIL-ADMIN] to=%s note=%s" % (ADMIN_EMAIL, admin_note))
        r["status"] = "ok"
        r["oid"] = oid
        r["txn"] = pay_result["txn"]
        r["total"] = grand
        return r

    def get_report(self, a):
        global orders_table, users_table, products_table, audit_table, x
        out = {}
        if a == "sales":
            tot = 0.0
            cnt = 0
            by_method = {}
            by_cat = {}
            for o in orders_table:
                tot += o["grand"]
                cnt += 1
                m = o["pay_method"]
                by_method[m] = by_method.get(m, 0.0) + o["grand"]
                for ii in o["items"]:
                    for pp in products_table:
                        if pp["pid"] == ii["pid"]:
                            cat = pp["cat"]
                            by_cat[cat] = by_cat.get(cat, 0.0) + ii["line_total"]
            out = {"total_revenue": tot, "order_count": cnt, "by_method": by_method, "by_cat": by_cat}
        elif a == "inventory":
            low = []
            out_of = []
            total_val = 0.0
            for p in products_table:
                total_val += p["price"] * p["qty"]
                if p["qty"] == 0:
                    out_of.append(p["pid"])
                elif p["qty"] < 10:
                    low.append(p["pid"])
            out = {"total_value": total_val, "low_stock": low, "out_of_stock": out_of, "product_count": len(products_table)}
        elif a == "users":
            active = 0
            inactive = 0
            by_region = {}
            for u in users_table:
                if u["active"] == 1:
                    active += 1
                else:
                    inactive += 1
                r2 = u["region"]
                by_region[r2] = by_region.get(r2, 0) + 1
            out = {"active": active, "inactive": inactive, "total": len(users_table), "by_region": by_region}
        elif a == "audit":
            by_action = {}
            for entry in audit_table:
                ac = entry["action"]
                by_action[ac] = by_action.get(ac, 0) + 1
            out = {"total_events": len(audit_table), "by_action": by_action, "total_ops": x}
        else:
            out = {"err": "unknown report type"}
        return out


def process_everything(uid, items, pay_method, addr, promo=None):
    sys = EnterpriseSystem()
    return sys.process_everything(uid, items, pay_method, addr, promo)


def bootstrap():
    global users_table, products_table
    sys = EnterpriseSystem()

    r1 = sys.create_user("Alice Johnson", "password1", "alice@example.com", "US", "5551234567", "admin")
    r2 = sys.create_user("Bob Smith", "password2", "bob@example.com", "UK", "441234567890", "customer")
    r3 = sys.create_user("Carol White", "password3", "carol@example.com", "IN", "9876543210", "customer")

    p1 = sys.add_product("Laptop Pro 15", "SKU-LPT-001", 1299.99, "electronics", 50, "WH-EAST")
    p2 = sys.add_product("Wireless Mouse", "SKU-MSE-002", 29.99, "electronics", 200, "WH-EAST")
    p3 = sys.add_product("USB-C Hub 7-in-1", "SKU-HUB-003", 49.99, "electronics", 150, "WH-WEST")
    p4 = sys.add_product("Standing Desk", "SKU-DSK-004", 399.99, "hardware", 30, "WH-CENTRAL")
    p5 = sys.add_product("Office Chair Ergo", "SKU-CHR-005", 249.99, "hardware", 45, "WH-CENTRAL")

    uid1 = r1.get("uid")
    pid1 = p1.get("pid")
    pid2 = p2.get("pid")

    addr1 = {
        "street": "123 Main St",
        "city": "Springfield",
        "zip": "62701",
        "card": {"number": "4111111111111111", "cvv": "123", "expiry": "12/26"},
    }

    order = sys.process_everything(
        uid1,
        [{"pid": pid1, "qty": 1}, {"pid": pid2, "qty": 2}],
        "card",
        addr1,
        "SAVE10",
    )
    print("\n[ORDER RESULT]", json.dumps(order, indent=2))
    print("\n[SALES REPORT]", json.dumps(sys.get_report("sales"), indent=2))
    print("\n[INVENTORY REPORT]", json.dumps(sys.get_report("inventory"), indent=2))
    print("\n[USER REPORT]", json.dumps(sys.get_report("users"), indent=2))
    print("\n[AUDIT REPORT]", json.dumps(sys.get_report("audit"), indent=2))


if __name__ == "__main__":
    bootstrap()