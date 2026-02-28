from ortools.sat.python import cp_model

# -----------------------------
# Ορισμός δεδομένων (ΜΕΡΟΣ Α1)
# -----------------------------
students = ["S1", "S2", "S3", "S4", "S5"]
courses = ["Math", "Physics", "CS_Lecture", "CS_Lab", "History", "Economics"]
rooms = ["R1", "R2", "R3"]
times = ["Mon_9", "Mon_11", "Tue_9", "Tue_11", "Wed_9"]

# Χωρητικότητα αιθουσών
room_capacity = {"R1": 30, "R2": 20, "R3": 15}

# Εγγεγραμμένοι φοιτητές ανά μάθημα
course_students = {
    "Math": ["S1", "S2", "S3"],
    "Physics": ["S2", "S3", "S4"],
    "CS_Lecture": ["S1", "S4", "S5"],
    "CS_Lab": ["S1", "S4", "S5"],
    "History": ["S1", "S2"],
    "Economics": ["S3", "S5"]
}

# Διαθεσιμότητα διδασκόντων (μάθημα -> ώρες που μπορεί)
teacher_availability = {
    "Math": ["Mon_9", "Tue_9"],
    "Physics": ["Mon_11", "Tue_11"],
    "CS_Lecture": ["Wed_9", "Mon_9"],
    "CS_Lab": ["Tue_11", "Wed_9"],
    "History": ["Mon_9", "Mon_11"],
    "Economics": ["Tue_9", "Wed_9"]
}

# Χρονικές εξαρτήσεις: η διάλεξη προηγείται του εργαστηρίου
prerequisites = [("CS_Lecture", "CS_Lab")]

# -------------------------------------
# Μοντελοποίηση μεταβλητών (ΜΕΡΟΣ Α2)
# -------------------------------------
model = cp_model.CpModel()

# Δυαδική μεταβλητή x[c, r, t] = 1 αν το μάθημα c διδάσκεται στην αίθουσα r την ώρα t
x = {}
for c in courses:
    for r in rooms:
        for t in times:
            x[c, r, t] = model.NewBoolVar(f"x[{c},{r},{t}]")

# -----------------------------
# Περιορισμοί (ΜΕΡΟΣ Α3)
# -----------------------------

# 1. Κάθε μάθημα προγραμματίζεται ακριβώς μία φορά
for c in courses:
    model.Add(sum(x[c, r, t] for r in rooms for t in times) == 1)

# 2. Μοναδική χρήση αίθουσας ανά ώρα
for r in rooms:
    for t in times:
        model.Add(sum(x[c, r, t] for c in courses) <= 1)

# 3. Χωρητικότητα αιθουσών
for c in courses:
    needed = len(course_students[c])
    for r in rooms:
        for t in times:
            model.Add(x[c, r, t] * needed <= room_capacity[r])

# 4. Διαθεσιμότητα διδασκόντων
for c in courses:
    available_times = teacher_availability[c]
    model.Add(sum(x[c, r, t] for r in rooms for t in available_times) == 1)

# 5. Αποφυγή επικαλύψεων φοιτητών
for s in students:
    for t in times:
        enrolled_courses = [c for c in courses if s in course_students[c]]
        model.Add(sum(x[c, r, t] for c in enrolled_courses for r in rooms) <= 1)

# 6. Χρονικές εξαρτήσεις (π.χ. Διάλεξη πριν από Εργαστήριο)
for lec, lab in prerequisites:
    # Αν η διάλεξη είναι πριν το εργαστήριο -> ο δείκτης ώρας πρέπει να είναι μικρότερος
    for r1 in rooms:
        for r2 in rooms:
            for i, t1 in enumerate(times):
                for j, t2 in enumerate(times):
                    if i >= j:
                        model.Add(x[lec, r1, t1] + x[lab, r2, t2] <= 1)

# -----------------------------
# Επίλυση (ΜΕΡΟΣ Α5)
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10
result = solver.Solve(model)

# -----------------------------
# Εμφάνιση αποτελεσμάτων
# -----------------------------
if result == cp_model.OPTIMAL or result == cp_model.FEASIBLE:
    print("✅ Εφικτή λύση βρέθηκε:\n")
    for c in courses:
        for r in rooms:
            for t in times:
                if solver.Value(x[c, r, t]) == 1:
                    print(f"{c:12s} -> {r} @ {t}")
else:
    print("❌ Δεν βρέθηκε εφικτή λύση.")
