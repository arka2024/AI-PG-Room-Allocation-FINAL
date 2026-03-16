import Layout from "../components/Layout";
import { useState } from "react";

function Reviews() {

const [rating,setRating] = useState(0);

function handleStarClick(value){
setRating(value);
}

return (

<Layout>

<section className="py-5" style={{marginTop:"70px"}}>

<div className="container">

<div className="row g-4">


{/* WRITE REVIEW */}

<div className="col-lg-5">

<div className="glass-card p-4" style={{position:"sticky",top:"90px"}}>

<h5 className="fw-bold mb-3">
Write a Review
</h5>

<form>

<label className="form-label fw-semibold">
Who are you reviewing?
</label>

<select className="form-select glass-input mb-3">

<option>Select a user...</option>
<option>Alex Smith</option>
<option>John Doe</option>
<option>Sarah Lee</option>

</select>


<label className="form-label fw-semibold">
Overall Rating
</label>

<div className="mb-3">

{[1,2,3,4,5].map((star)=>(
<i
key={star}
className={`bi fs-4 me-1 ${star<=rating ? "bi-star-fill text-warning" : "bi-star"}`}
style={{cursor:"pointer"}}
onClick={()=>handleStarClick(star)}
></i>
))}

</div>


<div className="row g-2 mb-3">

<div className="col-6">
<select className="form-select glass-input form-select-sm">
<option>Cleanliness</option>
<option>1 ⭐</option>
<option>2 ⭐</option>
<option>3 ⭐</option>
<option>4 ⭐</option>
<option>5 ⭐</option>
</select>
</div>

<div className="col-6">
<select className="form-select glass-input form-select-sm">
<option>Communication</option>
<option>1 ⭐</option>
<option>2 ⭐</option>
<option>3 ⭐</option>
<option>4 ⭐</option>
<option>5 ⭐</option>
</select>
</div>

</div>


<input
type="number"
className="form-control glass-input form-control-sm mb-3"
placeholder="Duration in months"
/>


<textarea
className="form-control glass-input mb-3"
rows="3"
placeholder="Share your experience..."
></textarea>


<div className="form-check form-switch mb-3">

<input
className="form-check-input"
type="checkbox"
defaultChecked
/>

<label className="form-check-label">
Would you recommend this person?
</label>

</div>


<button className="btn btn-accent w-100">

Submit Review

</button>

</form>

</div>

</div>



{/* RECENT REVIEWS */}

<div className="col-lg-7">

<h5 className="fw-bold mb-3">

Recent Reviews

</h5>


<div className="glass-card p-4 mb-3">

<div className="d-flex justify-content-between">

<div>

<strong>John Doe</strong>

<span className="text-muted mx-1">→</span>

<strong className="text-accent">
Alex Smith
</strong>

<br/>

<small className="text-muted">
March 10, 2026
</small>

</div>


<div className="text-warning">

⭐⭐⭐⭐

</div>

</div>


<p className="mt-2">

Very respectful and clean roommate.

</p>


<div className="d-flex gap-2">

<span className="badge bg-secondary bg-opacity-25">
🧹 Clean 4/5
</span>

<span className="badge bg-secondary bg-opacity-25">
💬 Comm 5/5
</span>

<span className="badge bg-secondary bg-opacity-25">
🤝 Respect 5/5
</span>

</div>

</div>



<div className="glass-card p-4 text-center">

<h5>No reviews yet</h5>

<p className="text-muted">
Be the first to review someone
</p>

</div>


</div>

</div>

</div>

</section>

</Layout>

)

}

export default Reviews;