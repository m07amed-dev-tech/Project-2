from datetime import datetime  # تأكد أن هذا السطر موجود في أول الملف فوق، أو اتركه هنا

def pay_installment_logic():
    student_id = entry_id.get()
    amount = entry_amount.get()
    if not student_id or not amount:
        lbl_status_pay.configure(text="⚠️ املأ خانات القسط!", text_color="#e74c3c")
        return
    try:
        s_id = int(student_id); pay_val = float(amount)
        if pay_val <= 0: return
        conn = sqlite3.connect("institute_v2.db")
        cursor = conn.cursor()
        
        # جلب بيانات الطالب الحالية (الاسم، المدفوع، المتبقي)
        cursor.execute("SELECT name, paid_fee, remaining_fee FROM students WHERE id = ?", (s_id,))
        student = cursor.fetchone()
        
        if student:
            s_name = student[0]
            current_paid = student[1]
            current_remaining = student[2]
            
            if pay_val > current_remaining:
                lbl_status_pay.configure(text="⚠️ المبلغ أكبر من المتبقي!", text_color="#e74c3c")
                conn.close(); return
                
            # 1. تحديث جدول الطلاب الأساسي (طرح القسط)
            new_paid = current_paid + pay_val
            new_remaining = current_remaining - pay_val
            cursor.execute("UPDATE students SET paid_fee = ?, remaining_fee = ? WHERE id = ?", (new_paid, new_remaining, s_id))
            
            # 2. السحر الجديد: التقاط الوقت الحالي بدقة وحقنه في السجل التاريخي
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO payments_log (student_id, student_name, amount_paid, payment_date)
                VALUES (?, ?, ?, ?)
            """, (s_id, s_name, pay_val, now_time))
            
            conn.commit()
            
            lbl_status_pay.configure(text=f"✓ تم دفع قسط {s_name} بنجاح", text_color="#2ecc71")
            entry_id.delete(0, ctk.END); entry_amount.delete(0, ctk.END)
            refresh_table()
        else:
            lbl_status_pay.configure(text="⚠️ رقم الطالب غير موجود!", text_color="#e74c3c")
        conn.close()
    except ValueError:
        lbl_status_pay.configure(text="⚠️ أدخل بيانات رقمية!", text_color="#e74c3c")
        
