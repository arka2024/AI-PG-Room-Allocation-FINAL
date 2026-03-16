import Layout from "../components/Layout";
import { useEffect } from "react";

function Map() {

useEffect(() => {

const userLat = 22.5726;
const userLng = 88.3639;

const map = window.L.map('discovery-map').setView([userLat, userLng], 13);

window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '© OpenStreetMap'
}).addTo(map);


window.L.marker([userLat, userLng]).addTo(map)
.bindPopup("<strong>Your Location</strong>");

let radiusCircle = null;
let markers = [];

function getColor(score){
if(score>=85) return "#22c55e";
if(score>=70) return "#eab308";
if(score>=50) return "#f97316";
return "#ef4444";
}

window.searchMap = function(){

const radius = document.getElementById("radiusSlider").value;
const minScore = document.getElementById("minScoreSlider").value;

markers.forEach(m => map.removeLayer(m));
markers=[];

if(radiusCircle) map.removeLayer(radiusCircle);

radiusCircle = window.L.circle([userLat,userLng],{
radius: radius*1000,
color:"#6366f1",
fillOpacity:0.05
}).addTo(map);

map.fitBounds(radiusCircle.getBounds());

fetch(`/api/map-search?radius=${radius}&min_score=${minScore}`)
.then(res=>res.json())
.then(data=>{

const resultsDiv = document.getElementById("mapResults");

if(data.results.length===0){
resultsDiv.innerHTML="No matches found";
return;
}

resultsDiv.innerHTML=`<h6>${data.results.length} matches found</h6>`;

data.results.forEach(r=>{

const color=getColor(r.score);

const marker=window.L.circleMarker([r.lat,r.lng],{
radius:10,
fillColor:color,
color:"#fff",
weight:2,
fillOpacity:0.9
}).addTo(map);

marker.bindPopup(`
<strong>${r.name}</strong><br>
${r.score}% Match<br>
${r.distance} km away
`);

markers.push(marker);

});
});

}

window.searchMap();

},[]);

return(

<Layout>

<section className="py-5" style={{marginTop:"70px"}}>

<div className="container-fluid px-4">

<div className="row g-3">


<div className="col-lg-3">

<div className="glass-card p-4">

<h5 className="fw-bold mb-3">
Geo-Spatial Discovery
</h5>

<p className="text-muted small">
Find compatible roommates near you
</p>


<label className="form-label fw-semibold">
Search Radius
</label>

<input
type="range"
className="form-range"
min="1"
max="50"
defaultValue="10"
id="radiusSlider"
/>


<label className="form-label fw-semibold mt-3">
Min Compatibility
</label>

<input
type="range"
className="form-range"
min="0"
max="100"
defaultValue="0"
id="minScoreSlider"
/>


<button
className="btn btn-accent w-100 mt-3"
onClick={()=>window.searchMap()}
>

Search Area

</button>


<div id="mapResults" className="mt-3">
</div>

</div>

</div>



<div className="col-lg-9">

<div
className="glass-card p-2"
style={{height:"calc(100vh - 120px)"}}
>

<div
id="discovery-map"
style={{height:"100%",borderRadius:"12px"}}
>

</div>

</div>

</div>


</div>

</div>

</section>

</Layout>

)

}

export default Map;