const express = require('express');
const fs = require('fs');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

let rawDealers = JSON.parse(fs.readFileSync('./data/dealerships.json','utf8'));
let dealerships = rawDealers.dealerships ? rawDealers.dealerships : rawDealers;

let rawReviews = JSON.parse(fs.readFileSync('./data/reviews.json','utf8'));
let reviews = rawReviews.reviews ? rawReviews.reviews : rawReviews;

app.get('/fetchDealers', (req,res)=> res.json(dealerships));
app.get('/fetchDealers/:state', (req,res)=> {
  let filtered = dealerships.filter(d=> d.state.toLowerCase() === req.params.state.toLowerCase());
  res.json(filtered);
});
app.get('/fetchDealer/:id', (req,res)=> {
  let dealer = dealerships.find(d=> d.id == req.params.id);
  res.json(dealer || {});
});
app.get('/fetchReviews', (req,res)=> res.json(reviews));
app.get('/fetchReviews/dealer/:id', (req,res)=> {
  let filtered = reviews.filter(r=> r.dealership == req.params.id);
  res.json(filtered);
});
app.post('/insertReview', (req,res)=> {
  reviews.push(req.body);
  let toSave = rawReviews.reviews ? {reviews} : reviews;
  fs.writeFileSync('./data/reviews.json', JSON.stringify(toSave, null, 2));
  res.json({status:"ok"});
});
app.listen(3030, ()=> console.log("Server is running on http://localhost:3030 - JSON MODE FIXED"));
