const mongoose = require('mongoose');

const teamSchema = new mongoose.Schema({
  name: { type: String, required: true, unique: true, index: true },
  matchesPlayed: { type: Number, default: 0 },
  wins: { type: Number, default: 0 },
  winPercentage: { type: Number, default: 0 },
  tossWins: { type: Number, default: 0 },
  tossMatchWins: { type: Number, default: 0 }, // Wins after winning toss
  battingFirstWins: { type: Number, default: 0 },
  chasingWins: { type: Number, default: 0 },
  seasonStats: [{
    season: { type: String },
    matchesPlayed: { type: Number, default: 0 },
    wins: { type: Number, default: 0 }
  }]
}, {
  timestamps: true
});

module.exports = mongoose.model('Team', teamSchema);
