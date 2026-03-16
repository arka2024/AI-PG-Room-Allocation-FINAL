import { useState } from "react";
import Layout from "../components/Layout";

function EditProfile() {

  const [formData, setFormData] = useState({
    full_name: "",
    age: "",
    gender: "male",
    occupation: "student",
    city: "",
    locality: "",
    bio: "",
    budget_min: "",
    budget_max: "",
    smoking: "never",
    drinking: "never",
    veg_nonveg: "nonveg",
    gender_preference: "any",
    pet_friendly: false,
    interests: ""
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(formData);

    // later connect to flask API
    // fetch("/api/edit-profile", { method:"POST" ... })
  };

  return (
    <Layout>

      <section className="py-5" style={{marginTop:"70px"}}>
        <div className="container">

          <div className="row justify-content-center">
            <div className="col-lg-10">

              <div className="glass-card p-4 p-lg-5">

                <h3 className="fw-bold mb-4">
                  Edit Your Profile
                </h3>

                <form onSubmit={handleSubmit}>

{/* BASIC INFO */}

<h5 className="fw-bold mb-3">Basic Info</h5>

<div className="row g-3 mb-4">

<div className="col-md-6">
<label className="form-label">Full Name</label>
<input
name="full_name"
value={formData.full_name}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

<div className="col-md-3">
<label className="form-label">Age</label>
<input
type="number"
name="age"
value={formData.age}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

<div className="col-md-3">
<label className="form-label">Gender</label>
<select
name="gender"
value={formData.gender}
onChange={handleChange}
className="form-select glass-input"
>
<option value="male">Male</option>
<option value="female">Female</option>
<option value="non-binary">Non-binary</option>
</select>
</div>

<div className="col-md-4">
<label className="form-label">Occupation</label>
<select
name="occupation"
value={formData.occupation}
onChange={handleChange}
className="form-select glass-input"
>
<option value="student">Student</option>
<option value="working_professional">Working Professional</option>
<option value="freelancer">Freelancer</option>
</select>
</div>

<div className="col-md-4">
<label className="form-label">City</label>
<input
name="city"
value={formData.city}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

<div className="col-md-4">
<label className="form-label">Locality</label>
<input
name="locality"
value={formData.locality}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

<div className="col-12">
<label className="form-label">Bio</label>
<textarea
name="bio"
rows="2"
value={formData.bio}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

</div>

{/* PREFERENCES */}

<h5 className="fw-bold mb-3">Preferences</h5>

<div className="row g-3 mb-4">

<div className="col-md-3">
<label className="form-label">Budget Min ₹</label>
<input
type="number"
name="budget_min"
value={formData.budget_min}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

<div className="col-md-3">
<label className="form-label">Budget Max ₹</label>
<input
type="number"
name="budget_max"
value={formData.budget_max}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

<div className="col-md-3">
<label className="form-label">Smoking</label>
<select
name="smoking"
value={formData.smoking}
onChange={handleChange}
className="form-select glass-input"
>
<option value="never">Never</option>
<option value="occasionally">Occasionally</option>
<option value="regularly">Regularly</option>
</select>
</div>

<div className="col-md-3">
<label className="form-label">Drinking</label>
<select
name="drinking"
value={formData.drinking}
onChange={handleChange}
className="form-select glass-input"
>
<option value="never">Never</option>
<option value="occasionally">Occasionally</option>
<option value="regularly">Regularly</option>
</select>
</div>

<div className="col-md-4">
<label className="form-label">Food</label>
<select
name="veg_nonveg"
value={formData.veg_nonveg}
onChange={handleChange}
className="form-select glass-input"
>
<option value="nonveg">Non-Veg</option>
<option value="veg">Vegetarian</option>
<option value="eggetarian">Eggetarian</option>
<option value="vegan">Vegan</option>
</select>
</div>

<div className="col-md-4">
<label className="form-label">Roommate Gender Pref</label>
<select
name="gender_preference"
value={formData.gender_preference}
onChange={handleChange}
className="form-select glass-input"
>
<option value="any">Any</option>
<option value="male">Male</option>
<option value="female">Female</option>
</select>
</div>

<div className="col-md-4 d-flex align-items-end">
<div className="form-check form-switch">
<input
type="checkbox"
name="pet_friendly"
checked={formData.pet_friendly}
onChange={handleChange}
className="form-check-input"
/>
<label className="form-check-label">
Pet Friendly 🐾
</label>
</div>
</div>

<div className="col-12">
<label className="form-label">
Interests (comma separated)
</label>
<input
name="interests"
value={formData.interests}
onChange={handleChange}
className="form-control glass-input"
/>
</div>

</div>

<button className="btn btn-accent px-4">
Save Changes
</button>

                </form>

              </div>

            </div>
          </div>

        </div>
      </section>

    </Layout>
  );
}

export default EditProfile;