import Layout from "../components/Layout";

function Search() {
  return (
    <Layout>

<section className="py-5" style={{marginTop:"70px"}}>
<div className="container">

<div className="row g-4">

{/* FILTERS */}

<div className="col-lg-3">
<div className="glass-card p-4 sticky-top" style={{top:"90px"}}>

<h5 className="fw-bold mb-3">
<i className="bi bi-funnel me-2 text-accent"></i>
Filters
</h5>

<form>

<div className="mb-3">
<label className="form-label small fw-semibold">Gender</label>
<select className="form-select glass-input form-select-sm">
<option>Any</option>
<option>Male</option>
<option>Female</option>
</select>
</div>

<div className="mb-3">
<label className="form-label small fw-semibold">Occupation</label>
<select className="form-select glass-input form-select-sm">
<option>Any</option>
<option>Student</option>
<option>Professional</option>
<option>Freelancer</option>
</select>
</div>

<div className="mb-3">
<label className="form-label small fw-semibold">Smoking</label>
<select className="form-select glass-input form-select-sm">
<option>Any</option>
<option>Never</option>
<option>Occasionally</option>
<option>Regularly</option>
</select>
</div>

<div className="mb-3">
<label className="form-label small fw-semibold">Food</label>
<select className="form-select glass-input form-select-sm">
<option>Any</option>
<option>Vegetarian</option>
<option>Non-Veg</option>
<option>Vegan</option>
</select>
</div>

<button className="btn btn-accent w-100 btn-sm">
<i className="bi bi-search me-1"></i>Search
</button>

</form>

</div>
</div>


{/* RESULTS */}

<div className="col-lg-9">

<div className="d-flex justify-content-between align-items-center mb-3">

<h4 className="fw-bold mb-0">
<i className="bi bi-search-heart text-accent me-2"></i>
AI-Ranked Matches
<span className="badge bg-secondary ms-2">12</span>
</h4>

<select className="form-select glass-input form-select-sm" style={{width:"auto"}}>
<option>Sort by Score</option>
<option>Sort by Distance</option>
</select>

</div>


{/* SAMPLE RESULT CARD */}

<div className="row g-3">

<div className="col-md-6">

<div className="glass-card p-4 h-100 search-result-card">

<div className="d-flex justify-content-between align-items-start mb-3">

<div className="d-flex align-items-center gap-3">

<div className="avatar-circle bg-primary">
AS
</div>

<div>
<h6 className="fw-bold mb-0">Alex Smith</h6>
<small className="text-muted">Student · 22y</small>
<br/>
<small className="text-muted">
<i className="bi bi-geo-alt"></i> Kolkata
</small>
</div>

</div>

<div className="text-center">
<span className="badge fs-5 bg-success">
92%
</span>
<br/>
<small className="text-muted">2km</small>
</div>

</div>


{/* TAGS */}

<div className="d-flex flex-wrap gap-1 mb-3">

<span className="badge bg-secondary bg-opacity-25 small">
🚬 Never
</span>

<span className="badge bg-secondary bg-opacity-25 small">
🍽️ Veg
</span>

<span className="badge bg-secondary bg-opacity-25 small">
🐾 Pet OK
</span>

<span className="badge bg-secondary bg-opacity-25 small">
⭐ 4.5
</span>

</div>


<div className="d-flex gap-2">

<a href="/profile" className="btn btn-outline-accent btn-sm flex-grow-1">
<i className="bi bi-person me-1"></i>
Profile
</a>

<a href="/compare" className="btn btn-outline-secondary btn-sm">
<i className="bi bi-bar-chart-line"></i>
</a>

</div>

</div>

</div>

</div>

</div>

</div>

</div>
</section>

</Layout>
  );
}

export default Search;