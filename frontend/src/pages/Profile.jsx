import Layout from "../components/Layout";

function Profile() {
  return (
    <Layout>

<section className="py-5" style={{marginTop:"70px"}}>
<div className="container">

<div className="row g-4">

{/* PROFILE CARD */}

<div className="col-lg-4">

<div className="glass-card p-4 text-center">

<div className="avatar-circle-lg bg-accent mx-auto mb-3">
AS
</div>

<h4 className="fw-bold mb-1">
Alex Smith
</h4>

<p className="text-muted mb-2">
Student · Age 22
</p>

<p className="text-muted mb-3">
<i className="bi bi-geo-alt me-1"></i>
Kolkata
</p>


<div className="compatibility-badge mb-3">

<div className="compat-circle high">

<span className="compat-value">
90%
</span>

<span className="compat-label">
Match
</span>

</div>

</div>


<div className="mb-3">

<span className="text-warning">
⭐⭐⭐⭐☆
</span>

<span className="ms-1">
4/5
</span>

</div>


<p className="text-muted small mb-3">
Friendly roommate who enjoys coding, gaming and music.
</p>


<div className="border-top border-secondary border-opacity-25 pt-3">

<div className="row g-2 text-start">

<div className="col-6">
<small className="text-muted">🚬 Non-smoker</small>
</div>

<div className="col-6">
<small className="text-muted">🍺 Occasionally</small>
</div>

<div className="col-6">
<small className="text-muted">🍽️ Veg</small>
</div>

<div className="col-6">
<small className="text-muted">🐾 Pet Friendly</small>
</div>

<div className="col-12">
<small className="text-muted">💰 ₹5000 - ₹9000 / month</small>
</div>

<div className="col-12">
<small className="text-muted">📅 Flexible Move-in</small>
</div>

</div>

</div>


<div className="border-top border-secondary border-opacity-25 pt-3 mt-3">

<h6 className="fw-bold mb-2">
Interests
</h6>

<div className="d-flex flex-wrap gap-1 justify-content-center">

<span className="badge bg-accent bg-opacity-10 text-accent">
Music
</span>

<span className="badge bg-accent bg-opacity-10 text-accent">
Gaming
</span>

<span className="badge bg-accent bg-opacity-10 text-accent">
Coding
</span>

</div>

</div>


<div className="mt-3 d-flex gap-2 justify-content-center">

<a href="/compare" className="btn btn-outline-accent btn-sm">
Compare
</a>

</div>

</div>

</div>


{/* DETAILS */}

<div className="col-lg-8">


<div className="glass-card p-4 mb-4">

<h5 className="fw-bold mb-3">

<i className="bi bi-bar-chart me-2"></i>

Lifestyle & Personality Profile

</h5>

<canvas height="200"></canvas>

</div>



<div className="glass-card p-4">

<h5 className="fw-bold mb-3">

<i className="bi bi-star me-2"></i>

Reviews

</h5>


<div className="border-bottom border-secondary border-opacity-25 pb-3 mb-3">

<div className="d-flex justify-content-between">

<div>
<strong>John Doe</strong>
<span className="text-warning ms-2">⭐⭐⭐⭐</span>
</div>

<small className="text-muted">
Jan 2024
</small>

</div>

<p className="text-muted small mt-1 mb-0">
Very clean and respectful roommate.
</p>

</div>



<div className="border-bottom border-secondary border-opacity-25 pb-3 mb-3">

<div className="d-flex justify-content-between">

<div>
<strong>Sarah Lee</strong>
<span className="text-warning ms-2">⭐⭐⭐⭐⭐</span>
</div>

<small className="text-muted">
Oct 2023
</small>

</div>

<p className="text-muted small mt-1 mb-0">
Great to live with and very friendly.
</p>

</div>


<a href="/reviews" className="btn btn-outline-accent btn-sm">

Write a Review

</a>

</div>


</div>

</div>

</div>
</section>

</Layout>
  );
}

export default Profile;