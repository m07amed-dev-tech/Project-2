import sqlite3
import customtkinter as ctk
from tkinter import messagebox

# ضبط المظهر العام للجيل الجديد
ctk.set_appearance_mode("dark")  # وضع مظلم تلقائي فخم
ctk.set_default_color_theme("blue")  # السمة اللونية الزرقاء الحديثة

# --- 1. قسم دالات قاعدة البيانات (Database Logic) ---

def init_db():
    conn = sqlite3.connect("institute_v2.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            total_fee REAL NOT NULL,
            paid_fee REAL NOT NULL,
            remaining_fee REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_student_logic():
    name = entry_name.get()
    course = entry_course.get()
    total = entry_total.get()
    paid = entry_paid.get()
    
    # فحص سريع للمدخلات لمنع انهيار البرنامج
    if not name or not course or not total or not paid:
        messagebox.showwarning("تنبيه", "الرجاء ملء جميع الخانات أولاً!")
        return
        
    try:
        total_val = float(total)
        paid_val = float(paid)
        remaining_val = total_val - paid_val
        
        conn = sqlite3.connect("institute_v2.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (name, course, total_fee, paid_fee, remaining_fee)
            VALUES (?, ?, ?, ?, ?)
        """, (name, course, total_val, paid_val, remaining_val))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("نجاح", f"تم تسجيل الطالب {name} بنجاح!\nالمتبقي عليه: {remaining_val} جنيه.")
        
        # تنظيف الخانات بعد الإدخال
        entry_name.delete(0, ctk.END)
        entry_course.delete(0, ctk.END)
        entry_total.delete(0, ctk.END)
        entry_paid.delete(0, ctk.END)
        
    except ValueError:
        messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة في خانات الرسوم والمدفوع!")

def pay_installment_logic():
    student_id = entry_id.get()
    amount = entry_amount.get()
    
    if not student_id or not amount:
        messagebox.showwarning("تنبيه", "الرجاء إدخال رقم الطالب ومبلغ القسط!")
        return
        
    try:
        s_id = int(student_id)
        pay_val = float(amount)
        
        conn = sqlite3.connect("institute_v2.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, paid_fee, remaining_fee FROM students WHERE id = ?", (s_id,))
        student = cursor.fetchone()
        
        if student:
            current_name = student[0]
            current_paid = student[1]
            current_remaining = student[2]
            
            if pay_val > current_remaining:
                messagebox.showwarning("تنبيه", f"المبلغ المدفوع أكبر من المتبقي على الطالب! المتبقي الحالي هو: {current_remaining}")
                conn.close()
                return
                
            new_paid = current_paid + pay_val
            new_remaining = current_remaining - pay_val
            
            cursor.execute("""
                UPDATE students 
                SET paid_fee = ?, remaining_fee = ? 
                WHERE id = ?
            """, (new_paid, new_remaining, s_id))
            conn.commit()
            
            messagebox.showinfo("نجاح", f"تم تسجيل القسط للطالب: {current_name}\nالمتبقي الجديد عليه: {new_remaining} جنيه.")
            entry_id.delete(0, ctk.END)
            entry_amount.delete(0, ctk.END)
        else:
            messagebox.showerror("خطأ", "لم يتم العثور على طالب بهذا الرقم (ID)!")
            
        conn.close()
    except ValueError:
        messagebox.showerror("خطأ", "الرجاء إدخال بيانات رقمية صحيحة!")

def show_reports_gui():
    conn = sqlite3.connect("institute_v2.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, remaining_fee FROM students WHERE remaining_fee > 0 ORDER BY name ASC")
    debtors = cursor.fetchall()
    
    debtors_text = ""
    if debtors:
        for row in debtors:
            debtors_text += f"👤 {row[0]} | المتبقي: {row[1]} جنيه\n"
    else:
        debtors_text = "🎉 لا يوجد طلاب متأخرين! الخزنة مستقرة.\n"
        
    cursor.execute("SELECT SUM(paid_fee) FROM students")
    total_in_safe = cursor.fetchone()[0]
    if total_in_safe is None:
        total_in_safe = 0
        
    conn.close()
    
    final_report = f"⚠️ الطلاب المتأخرين عن السداد (أبجدياً):\n{debtors_text}\n"
    final_report += f"----------------------------------------\n"
    final_report += f"💰 إجمالي الأموال في الخزينة حالياً: {total_in_safe} جنيه"
    
    messagebox.showinfo("📊 تقرير الجرد المالي للجيل الجديد", final_report)


# --- 2. قسم بناء الواجهة الرسومية الحديثة (CustomTkinter GUI) ---

init_db()  # تشغيل قاعدة البيانات أولاً تلقائياً

root = ctk.CTk()
root.title("🏢 نظام إدارة المعهد - جيل الواجهات الحديثة")
root.geometry("800x550")
root.resizable(False, False)

# العنوان الرئيسي الفخم
main_title = ctk.CTkLabel(root, text="🏢 نظام إدارة الحسابات والأقساط الذكي", font=("Arial", 22, "bold"))
main_title.pack(pady=15)

# الحاوية الكبرى لتقسيم الشاشة يمين ويسار بدون عشوائية
main_frame = ctk.CTkFrame(root, width=760, height=380, fg_color="transparent")
main_frame.pack(pady=10)

# --- الطرف الأيمن: تسجيل طالب جديد ---
frame_left = ctk.CTkFrame(main_frame, width=360, height=360, corner_radius=15)
frame_left.pack(side="right", padx=15, fill="both", expand=True)

lbl_add_title = ctk.CTkLabel(frame_left, text="➕ تسجيل طالب جديد", font=("Arial", 16, "bold"), text_color="#2ecc71")
lbl_add_title.pack(pady=10)

entry_name = ctk.CTkEntry(frame_left, placeholder_text="ادخل اسم الطالب الكامل", width=250, justify="right")
entry_name.pack(pady=8)

entry_course = ctk.CTkEntry(frame_left, placeholder_text="ادخل اسم المجال / الكورس", width=250, justify="right")
entry_course.pack(pady=8)

entry_total = ctk.CTkEntry(frame_left, placeholder_text="إجمالي رسوم الكورس", width=250, justify="right")
entry_total.pack(pady=8)

entry_paid = ctk.CTkEntry(frame_left, placeholder_text="المبلغ المدفوع حالياً", width=250, justify="right")
entry_paid.pack(pady=8)

btn_add = ctk.CTkButton(frame_left, text="حفظ وحساب البيانات", font=("Arial", 13, "bold"), fg_color="#2ecc71", hover_color="#27ae60", command=add_student_logic)
btn_add.pack(pady=15)


# --- الطرف الأيسر: دفع الأقساط والتقارير ---
frame_right = ctk.CTkFrame(main_frame, width=360, height=360, corner_radius=15)
frame_right.pack(side="left", padx=15, fill="both", expand=True)

lbl_pay_title = ctk.CTkLabel(frame_right, text="💵 إدارة ودفع الأقساط", font=("Arial", 16, "bold"), text_color="#3498db")
lbl_pay_title.pack(pady=10)

entry_id = ctk.CTkEntry(frame_right, placeholder_text="(ID) ادخل رقم الطالب", width=250, justify="right")
entry_id.pack(pady=8)

entry_amount = ctk.CTkEntry(frame_right, placeholder_text="مبلغ القسط المراد دفعه هسي", width=250, justify="right")
entry_amount.pack(pady=8)

btn_pay = ctk.CTkButton(frame_right, text="تسجيل عملية الدفع", font=("Arial", 13, "bold"), fg_color="#3498db", hover_color="#2980b9", command=pay_installment_logic)
btn_pay.pack(pady=12)

# خط فاصل بسيط ومحترم مظهر الحافة
separator = ctk.CTkFrame(frame_right, height=2, width=280, fg_color="gray")
separator.pack(pady=10)

# زر التقارير الجاهز بلمسة الجيل الجديد
btn_report = ctk.CTkButton(frame_right, text="📊 جرد الخزنة والتقارير", font=("Arial", 14, "bold"), fg_color="#f1c40f", text_color="black", hover_color="#f39c12", width=250, command=show_reports_gui)
btn_report.pack(pady=10)


# --- شريط السفلي للإغلاق ---
btn_exit = ctk.CTkButton(root, text="❌ إغلاق النظام بأمان", font=("Arial", 13, "bold"), fg_color="#e74c3c", hover_color="#c0392b", width=200, command=root.quit)
btn_exit.pack(pady=10)

root.mainloop()
