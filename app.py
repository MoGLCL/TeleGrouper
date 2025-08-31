from flask import Flask, render_template, request, redirect, url_for, session, flash
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError, PhoneCodeInvalidError, PhoneCodeExpiredError
from telethon.tl.functions.channels import CreateChannelRequest
import asyncio
import nest_asyncio
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import base64
from io import BytesIO
from functools import wraps
import uuid
import secrets

# =======================
nest_asyncio.apply()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
SESSION_FOLDER = "sessions"
os.makedirs(SESSION_FOLDER, exist_ok=True)
egypt_tz = ZoneInfo("Africa/Cairo")

# =======================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "phone" not in session:
            flash("يرجى تسجيل الدخول أولاً.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# =======================
async def create_groups_async(client, n, base_title, about, message, delay):
    # This function remains the same
    await client.connect()
    titles = [base_title if i==0 else f"{base_title}{i}" for i in range(n)]
    created = []
    for i, title in enumerate(titles, 1):
        result = await client(CreateChannelRequest(title=title, about=about, megagroup=True))
        chat = result.chats[-1]
        ts = datetime.now(egypt_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        final_msg = message.replace("{created_at}", ts)
        await client.send_message(chat, final_msg)
        created.append(f"{title} ({ts})")
        if i < n:
            await asyncio.sleep(delay)
    await client.disconnect()
    return created

# =======================
async def get_user_info(client):
    # This function remains the same
    await client.connect()
    me = await client.get_me()
    try:
        bio_bytes = await client.download_profile_photo(me, file=BytesIO())
        bio_bytes.seek(0)
        photo_b64 = base64.b64encode(bio_bytes.read()).decode('utf-8')
    except TypeError:
        photo_b64 = None
    await client.disconnect()
    return {
        "id": me.id,
        "username": me.username,
        "first_name": me.first_name,
        "last_name": me.last_name,
        "phone": me.phone,
        "photo": photo_b64
    }

# =======================
def get_session_name():
    # This function remains the same
    if "flask_id" not in session:
        session["flask_id"] = str(uuid.uuid4())
    return os.path.join(SESSION_FOLDER, f"{session['flask_id']}-{session['phone'].replace('+','')}")

# =======================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            session["api_id"] = int(request.form["api_id"])
        except (ValueError, TypeError):
            flash("API ID must be a number.", "danger")
            return render_template("login.html")
        session["api_hash"] = request.form["api_hash"]
        session["phone"] = request.form["phone"]
        session_name = get_session_name()
        client = TelegramClient(session_name, session["api_id"], session["api_hash"])
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def send_code():
            await client.connect()
            if not await client.is_user_authorized():
                try:
                    result = await client.send_code_request(session["phone"])
                    session['phone_code_hash'] = result.phone_code_hash
                    flash("تم إرسال كود الدخول إلى حسابك في تليجرام.", "success")
                except FloodWaitError as e:
                    flash(f"لقد حاولت كثيراً. من فضلك انتظر {e.seconds} ثانية.", "danger")
                except Exception as e:
                    error_text = str(e)
                    if "api_id/api_hash combination is invalid" in error_text:
                        flash("البيانات المدخلة (API ID أو API Hash) غير صحيحة. يرجى التحقق منها.", "danger")
                    else:
                        print(f"DEBUG - An unexpected error occurred in login: {e}")
                        flash("حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.", "danger")
            await client.disconnect()
        try:
            loop.run_until_complete(send_code())
        finally:
            loop.close()
        return redirect(url_for("verify_code"))
    return render_template("login.html")

# =======================
# --- تم إعادة بناء هذه الدالة بالكامل لتكون أكثر استقرارًا ---
@app.route("/verify", methods=["GET", "POST"])
@login_required
def verify_code():
    if request.method == "POST":
        code = request.form["code"]
        session_name = get_session_name()
        client = TelegramClient(session_name, session["api_id"], session["api_hash"])
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def sign_in_with_code():
            await client.connect()
            try:
                phone_code_hash = session.get('phone_code_hash')
                if not phone_code_hash:
                    flash("انتهت صلاحية جلستك، يرجى تسجيل الدخول مرة أخرى.", "warning")
                    return 'FAILURE'
                await client.sign_in(session["phone"], code, phone_code_hash=phone_code_hash)
                return 'SUCCESS'
            except SessionPasswordNeededError:
                return 'NEEDS_PASSWORD'
            except PhoneCodeInvalidError:
                flash("الكود الذي أدخلته غير صحيح. يرجى المحاولة مرة أخرى.", "danger")
                return 'FAILURE'
            except PhoneCodeExpiredError:
                flash("انتهت صلاحية هذا الكود. يرجى تسجيل الدخول مرة أخرى للحصول على كود جديد.", "danger")
                return 'FAILURE'
            except Exception as e:
                print(f"DEBUG - An error occurred during sign-in: {e}")
                flash(f"حدث خطأ غير متوقع أثناء التحقق: {e}", "danger")
                return 'FAILURE'
            finally:
                if client.is_connected():
                    await client.disconnect()
        status = loop.run_until_complete(sign_in_with_code())
        loop.close()
        if status == 'SUCCESS':
            session.pop('phone_code_hash', None)
            return redirect(url_for("groups"))
        elif status == 'NEEDS_PASSWORD':
            session.pop('phone_code_hash', None)
            return redirect(url_for("enter_password"))
        else: # FAILURE
            return redirect(url_for("login"))
    return render_template("code.html", password_required=False)

# =======================
@app.route("/password", methods=["GET", "POST"])
@login_required
def enter_password():
    # This function remains the same
    if request.method == "POST":
        password = request.form["password"]
        session_name = get_session_name()
        client = TelegramClient(session_name, session["api_id"], session["api_hash"])
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def login_password():
            await client.connect()
            try:
                await client.sign_in(password=password)
            except Exception as e:
                print(f"DEBUG - An error occurred during password sign-in: {e}")
                flash(f"كلمة المرور غير صحيحة أو حدث خطأ: {e}", "danger")
                return redirect(url_for("enter_password"))
            finally:
                if client.is_connected():
                    await client.disconnect()
        try:
            loop.run_until_complete(login_password())
        finally:
            loop.close()
        return redirect(url_for("groups"))
    return render_template("code.html", password_required=True)

# =======================
@app.route("/groups", methods=["GET", "POST"])
@login_required
def groups():
    # This function remains the same
    session_name = get_session_name()
    client = TelegramClient(session_name, session["api_id"], session["api_hash"])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    user_info = {}
    try:
        user_info = loop.run_until_complete(get_user_info(client))
    except Exception as e:
        print(f"DEBUG - Could not get user info: {e}")
        flash("حدث خطأ أثناء جلب معلومات المستخدم. قد تحتاج إلى تسجيل الدخول مرة أخرى.", "warning")
        return redirect(url_for("login"))
    if request.method == "POST":
        try:
            n = int(request.form["n"])
            base_title = request.form["base_title"]
            about = request.form["about"]
            message = request.form["message"]
            delay = int(request.form["delay"])
            created = loop.run_until_complete(
                create_groups_async(client, n, base_title, about, message, delay)
            )
            return render_template("result.html", created=created)
        except Exception as e:
            print(f"DEBUG - Error during group creation: {e}")
            flash(f"حدث خطأ أثناء إنشاء المجموعات: {e}", "danger")
        finally:
            loop.close()
            return render_template("groups.html", user_info=user_info)
    loop.close()
    return render_template("groups.html", user_info=user_info)

# =======================
if __name__ == "__main__":
    app.run(debug=True)