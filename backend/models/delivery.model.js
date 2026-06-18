const mongoose = require('mongoose');

const deliverySchema = new mongoose.Schema({
  matchId: { type: Number, required: true, index: true },
  inning: { type: Number, required: true },
  battingTeam: { type: String, required: true, index: true },
  bowlingTeam: { type: String, required: true, index: true },
  over: { type: Number, required: true },
  ball: { type: Number, required: true },
  batter: { type: String, required: true, index: true },
  bowler: { type: String, required: true, index: true },
  nonStriker: { type: String },
  batsmanRuns: { type: Number, default: 0 },
  extraRuns: { type: Number, default: 0 },
  totalRuns: { type: Number, default: 0 },
  extrasType: { type: String },
  isWicket: { type: Number, default: 0 },
  playerDismissed: { type: String },
  dismissalKind: { type: String },
  fielder: { type: String }
}, {
  timestamps: false // Disable timestamps for size/performance
});

module.exports = mongoose.model('Delivery', deliverySchema);
