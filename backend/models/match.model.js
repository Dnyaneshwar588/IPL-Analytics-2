const mongoose = require('mongoose');

const matchSchema = new mongoose.Schema({
  matchId: { type: Number, required: true, unique: true, index: true },
  season: { type: String, required: true, index: true },
  city: { type: String },
  date: { type: Date, required: true },
  matchType: { type: String },
  playerOfMatch: { type: String },
  venue: { type: String, index: true },
  team1: { type: String, required: true, index: true },
  team2: { type: String, required: true, index: true },
  tossWinner: { type: String },
  tossDecision: { type: String },
  winner: { type: String, index: true },
  result: { type: String },
  resultMargin: { type: Number },
  targetRuns: { type: Number },
  targetOvers: { type: Number },
  superOver: { type: String },
  method: { type: String },
  umpire1: { type: String },
  umpire2: { type: String }
}, {
  timestamps: true
});

module.exports = mongoose.model('Match', matchSchema);
