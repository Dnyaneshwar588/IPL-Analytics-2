const mongoose = require('mongoose');

const playerSchema = new mongoose.Schema({
  name: { type: String, required: true, unique: true, index: true },
  roles: [{ type: String }],
  battingStats: {
    runs: { type: Number, default: 0 },
    balls: { type: Number, default: 0 },
    dismissals: { type: Number, default: 0 },
    average: { type: Number, default: 0 },
    strikeRate: { type: Number, default: 0 },
    fours: { type: Number, default: 0 },
    sixes: { type: Number, default: 0 }
  },
  bowlingStats: {
    balls: { type: Number, default: 0 },
    runsConceded: { type: Number, default: 0 },
    wickets: { type: Number, default: 0 },
    economy: { type: Number, default: 0 },
    average: { type: Number, default: 0 }
  },
  fieldingStats: {
    catches: { type: Number, default: 0 },
    stumpings: { type: Number, default: 0 },
    runOuts: { type: Number, default: 0 }
  },
  fantasyPoints: { type: Number, default: 0 }
}, {
  timestamps: true
});

// Create compound indexes to query top batsmen and bowlers quickly
playerSchema.index({ 'battingStats.runs': -1 });
playerSchema.index({ 'bowlingStats.wickets': -1 });

module.exports = mongoose.model('Player', playerSchema);
