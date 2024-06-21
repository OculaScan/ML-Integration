from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)
from db import (
    db,
    UserModel,
)
from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename
import tensorflow as tf
import os
from PIL import Image
import numpy as np

# App
app = Flask(__name__)
app.secret_key = "buat_secret_key_lebih_rumit"

# Load model
model = tf.keras.models.load_model('MobileNet_TrainTestVal_ACC91%.h5')

# Mendefinisikan classes dan deskripsinya
classes = ["cataract", "diabetic_retinopathy", "glaucoma", "normal"]
class_descriptions = {
    "cataract": "Cataract adalah kekeruhan pada lensa mata, yang menyebabkan penurunan penglihatan.",
    "diabetic_retinopathy": "Diabetic retinopathy adalah komplikasi diabetes yang memengaruhi mata.",
    "glaucoma": "Glaucoma adalah sekelompok kondisi mata yang merusak saraf optik.",
    "normal": "Normal mata, tidak memiliki tanda-tanda katarak, retinopati diabetik, atau glaukoma."
}

# Tentukan ekstensi file yang diizinkan
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Berfungsi untuk memeriksa apakah ekstensi file diperbolehkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Konfigurasi SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql://root:@localhost/flask_deteksipenyakitmata"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)  # Inisialisasi SQLAlchemy dengan aplikasi Flask

# Buat direktori untuk menyimpan file upload jika belum ada
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# menampilkan data
@app.route("/")
def home():
    return render_template("user/index.html")

# menampilkan halaman admin
@app.route("/admin/image-clasification")
def admin():
    return render_template("admin/imageClasification.html", title="Image Clasification")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html", title="Register")
    else:
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Mengenkripsi password sebelum disimpan
        hashed_password = generate_password_hash(password)

        # Membuat objek User baru
        new_user = UserModel(name=name, email=email, password=hashed_password)

        # Menyimpan objek User ke dalam database
        db.session.add(new_user)
        db.session.commit()

        session["name"] = name
        session["email"] = email
        return redirect(url_for("allNew"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == ("POST"):
        email = request.form["email"]
        password = request.form["password"]

        # Mencari pengguna berdasarkan alamat email
        user = db.session.query(UserModel).filter_by(email=email).first()

        if user:
            # Memeriksa kata sandi
            if check_password_hash(user.password, password):
                # Jika kata sandi cocok, atur sesi dan arahkan ke halaman yang sesuai
                session["name"] = user.name
                session["email"] = user.email
                return redirect(url_for("allNew"))
            else:
                # Jika kata sandi tidak cocok, beri pesan kesalahan
                flash("Gagal, Email dan Password Tidak Cocok")
                return redirect(url_for("login"))
        else:
            # Jika pengguna tidak ditemukan, beri pesan kesalahan
            flash("Gagal, Email tidak terdaftar")
            return redirect(url_for("login"))
    else:
        return render_template("auth/login.html", title="Login")
    
# Route untuk menangani image upload dan classification
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            # Preprocess the image
            img = Image.open(filepath).convert('RGB')
            img = img.resize((256, 256))
            img = np.array(img) / 255.0
            img = np.expand_dims(img, axis=0)

            # Perform classification
            predictions = model.predict(img)
            predicted_class = np.argmax(predictions)
            predicted_label = classes[predicted_class]
            accuracy = predictions[0][predicted_class] * 100

            # Get description for predicted label
            description = class_descriptions[predicted_label]

            return jsonify({
                'predicted_label': predicted_label,
                'description': description,
                'accuracy': f"{accuracy:.2f}%"
            })

        except Exception as e:
            return jsonify({'error': str(e)})

    else:
        return jsonify({'error': 'File type not allowed'})

if __name__ == "__main__":
    app.run(debug=True)
