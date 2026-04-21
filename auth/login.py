import streamlit as st
import sqlite3
from db.database import get_db, verify_password, hash_password

# ---------------- LOGIN ----------------
def check_user_credentials(username, password):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT password, role FROM users WHERE username=?", (username,))
    result = cur.fetchone()
    conn.close()

    if result:
        stored_password, role = result

        if verify_password(stored_password, password):
            return role
        
    return None

# ---------------- REGISTER ----------------
def register_user(username, password):
    conn = get_db()
    cur = conn.cursor()

    try:
        hashed = hash_password(password)
        cur.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed, "user"))
        conn.commit()
        return True, "Kayıt başarılı"
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı zaten var"
    finally:
        conn.close()


# ---------------- UI ----------------
def login_page():
    st.title("Giriş / Kayıt")

    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    # -------- LOGIN --------
    with tab1:
        with st.form("login"):
            user = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")

            if st.form_submit_button("Giriş"):
                role = check_user_credentials(user, pw)

                if role:
                    st.session_state.logged_in = True
                    st.session_state.user_role = role
                    st.session_state.username = user  # 🔥 kritik
                    st.rerun()
                else:
                    st.error("Hatalı giriş!")

    # -------- REGISTER --------
    with tab2:
        with st.form("register"):
            new_user = st.text_input("Kullanıcı Adı", key="reg_user")
            new_pw = st.text_input("Şifre", type="password", key="reg_pw")

            if st.form_submit_button("Kayıt Ol"):
                success, msg = register_user(new_user, new_pw)

                if success:
                    st.success(msg)
                else:
                    st.error(msg)