import Layout from "../components/Layout";
import { useEffect } from "react";
import Chart from "chart.js/auto";

function Compare() {

useEffect(()=>{

const radar = document.getElementById("compareRadar");
const bar = document.getElementById("diffBar");

if(!radar || !bar) return;

const vecA = [4,3,5,2,4];
const vecB = [3,4,4,3,5];

const labels = [
"Cleanliness",
"Communication",
"Sleep Schedule",
"Social",
"Noise"
];

new Chart(radar,{
type:"radar",
data:{
labels:labels,
datasets:[
{
label:"User A",
data:vecA,
backgroundColor:"rgba(99,102,241,0.2)",
borderColor:"rgba(99,102,241,1)",
borderWidth:2
},
{
label:"User B",
data:vecB,
backgroundColor:"rgba(34,211,238,0.2)",
borderColor:"rgba(34,211,238,1)",
borderWidth:2
}
]
},
options:{
scales:{
r:{
min:0,
max:5,
ticks:{stepSize:1}
}
}
}
});


new Chart(bar,{
type:"bar",
data:{
labels:labels,
datasets:[
{
label:"Difference",
data:[1,1,1,1,1],
backgroundColor:"rgba(34,197,94,0.7)"
}
]
},
options:{
indexAxis:"y"
}
});

},[]);


return(

<Layout>

<section className="py-5" style={{marginTop:"70px"}}>

<div className="container">

<h3 className="fw-bold mb-4">
Comparative Analysis Tool
</h3>


<div className="glass-card p-4 mb-4">

<div className="row g-3">

<div className="col-md-4">

<label className="form-label fw-semibold">
User A
</label>

<select className="form-select glass-input">
<option>You</option>
<option>Alex Smith</option>
<option>John Doe</option>
</select>

</div>


<div className="col-md-4">

<label className="form-label fw-semibold">
User B
</label>

<select className="form-select glass-input">
<option>Select user</option>
<option>Sarah Lee</option>
<option>John Doe</option>
</select>

</div>


<div className="col-md-4 d-flex align-items-end">

<button className="btn btn-accent w-100">

Compare

</button>

</div>

</div>

</div>



<div className="glass-card p-4 mb-4 text-center">

<div className="row align-items-center">

<div className="col-md-4">

<div className="avatar-circle-lg bg-primary mx-auto mb-2">
UA
</div>

<h5>User A</h5>

</div>


<div className="col-md-4">

<div className="compat-circle high mx-auto">

<span className="compat-value">
82%
</span>

<span className="compat-label">
Compatible
</span>

</div>

</div>


<div className="col-md-4">

<div className="avatar-circle-lg bg-info mx-auto mb-2">
UB
</div>

<h5>User B</h5>

</div>

</div>

</div>



<div className="row g-4">


<div className="col-lg-6">

<div className="glass-card p-4">

<h5 className="fw-bold mb-3">
Profile Overlay
</h5>

<canvas id="compareRadar"></canvas>

</div>

</div>


<div className="col-lg-6">

<div className="glass-card p-4">

<h5 className="fw-bold mb-3">
Feature Differential
</h5>

<canvas id="diffBar"></canvas>

</div>

</div>


<div className="col-md-6">

<div className="glass-card p-4">

<h5 className="fw-bold mb-3">
Top Overlaps
</h5>

<p className="text-muted">
Cleanliness, communication and lifestyle preferences are very similar.
</p>

</div>

</div>


<div className="col-md-6">

<div className="glass-card p-4">

<h5 className="fw-bold mb-3">
Top Conflicts
</h5>

<p className="text-muted">
Noise level preference and sleep schedule differ slightly.
</p>

</div>

</div>


<div className="col-12">

<div className="glass-card p-4">

<h5 className="fw-bold mb-3">
Pre-Move-in Discussion Guide
</h5>

<p className="text-muted">

Discuss cleaning schedule, guest policies, and noise tolerance before moving in together.

</p>

</div>

</div>


</div>

</div>

</section>

</Layout>

)

}

export default Compare;