const express = require('express');
const router = express.Router();
const axios = require('axios');
const Match = require('../models/match.model');
const Delivery = require('../models/delivery.model');
const Team = require('../models/team.model');
const Player = require('../models/player.model');

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

const VALID_WICKET_KINDS = [
  'bowled',
  'caught',
  'lbw',
  'stumped',
  'caught and bowled',
  'hit wicket'
];

// 1. Teams Route
router.get('/teams', async (req, res) => {
  try {
    const teams = await Team.find().sort({ wins: -1 });
    res.json(teams);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 2. Players Route (Search, Sort, Filters)
router.get('/players', async (req, res) => {
  try {
    const { search, role, sort, limit = 10 } = req.query;
    const query = {};

    if (search) {
      query.name = { $regex: search, $options: 'i' };
    }
    if (role) {
      query.roles = role;
    }

    let sortOption = { 'battingStats.runs': -1 }; // default
    if (sort === 'runs') {
      sortOption = { 'battingStats.runs': -1 };
    } else if (sort === 'wickets') {
      sortOption = { 'bowlingStats.wickets': -1 };
    } else if (sort === 'sr') {
      sortOption = { 'battingStats.strikeRate': -1 };
    } else if (sort === 'econ') {
      sortOption = { 'bowlingStats.economy': 1 };
    } else if (sort === 'fantasy') {
      sortOption = { fantasyPoints: -1 };
    }

    const players = await Player.find(query)
      .sort(sortOption)
      .limit(parseInt(limit));

    res.json(players);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 3. Venues Route (Avg Scores, Win Rates, Heatmap data)
router.get('/venues', async (req, res) => {
  try {
    const matches = await Match.find();
    
    // Aggregate venue data in-memory (fast for 1096 documents)
    const venueStats = {};

    for (const match of matches) {
      const v = match.venue;
      if (!venueStats[v]) {
        venueStats[v] = {
          venue: v,
          matchesPlayed: 0,
          batFirstWins: 0,
          chasingWins: 0,
          totalResultMargin: 0,
          noResults: 0
        };
      }

      const stats = venueStats[v];
      stats.matchesPlayed++;

      if (match.winner === 'No Result' || !match.winner) {
        stats.noResults++;
        continue;
      }

      const batFirst = match.tossDecision === 'bat' ? match.tossWinner : (match.tossWinner === match.team1 ? match.team2 : match.team1);
      if (match.winner === batFirst) {
        stats.batFirstWins++;
      } else {
        stats.chasingWins++;
      }
    }

    // Now compute averages
    const result = await Promise.all(Object.values(venueStats).map(async (v) => {
      // Find average first innings score for each venue
      const pipeline = [
        { $match: { venue: v.venue } },
        {
          $lookup: {
            from: 'deliveries',
            localField: 'matchId',
            foreignField: 'matchId',
            as: 'deliveries'
          }
        },
        { $unwind: '$deliveries' },
        { $match: { 'deliveries.inning': 1 } },
        { $group: { _id: '$matchId', totalRuns: { $sum: '$deliveries.totalRuns' } } },
        { $group: { _id: null, avgScore: { $avg: '$totalRuns' } } }
      ];

      const avgRes = await Match.aggregate(pipeline);
      const avgScore = avgRes.length > 0 ? Math.round(avgRes[0].avgScore) : 160;

      const validWins = v.batFirstWins + v.chasingWins;
      const batFirstWinPct = validWins > 0 ? parseFloat((v.batFirstWins / validWins * 100).toFixed(2)) : 50;

      return {
        venue: v.venue,
        matchesPlayed: v.matchesPlayed,
        batFirstWins: v.batFirstWins,
        chasingWins: v.chasingWins,
        batFirstWinPct,
        avgFirstInningsScore: avgScore
      };
    }));

    // Sort by matches played descending
    result.sort((a, b) => b.matchesPlayed - a.matchesPlayed);

    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 4. Batter vs Bowler Matchup Route
router.get('/matchup', async (req, res) => {
  try {
    const { batsman, bowler } = req.query;
    if (!batsman || !bowler) {
      return res.status(400).json({ error: 'batsman and bowler query parameters are required.' });
    }

    const deliveries = await Delivery.find({ batter: batsman, bowler: bowler });

    if (deliveries.length === 0) {
      return res.json({
        runs: 0,
        balls: 0,
        dismissals: 0,
        fours: 0,
        sixes: 0,
        dots: 0,
        strikeRate: 0,
        message: 'No head-to-head records found.'
      });
    }

    let runs = 0;
    let balls = 0;
    let dismissals = 0;
    let fours = 0;
    let sixes = 0;
    let dots = 0;

    for (const d of deliveries) {
      runs += d.batsmanRuns;
      if (d.extrasType !== 'wides') {
        balls++;
      }
      if (d.batsmanRuns === 4) fours++;
      if (d.batsmanRuns === 6) sixes++;
      if (d.batsmanRuns === 0 && d.extraRuns === 0) dots++;
      
      if (d.playerDismissed === batsman && VALID_WICKET_KINDS.includes(d.dismissalKind.toLowerCase().trim())) {
        dismissals++;
      }
    }

    const strikeRate = balls > 0 ? parseFloat((runs / balls * 100).toFixed(2)) : 0;

    res.json({
      runs,
      balls,
      dismissals,
      fours,
      sixes,
      dots,
      strikeRate
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 5. Predict Winner Endpoint (Forwards to FastAPI)
router.post('/predict', async (req, res) => {
  try {
    const response = await axios.post(`${ML_SERVICE_URL}/predict/winner`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'FastAPI prediction error',
      details: error.response?.data || error.message
    });
  }
});

// 6. Predict Score Endpoint (Forwards to FastAPI)
router.post('/predict/score', async (req, res) => {
  try {
    const response = await axios.post(`${ML_SERVICE_URL}/predict/score`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'FastAPI score prediction error',
      details: error.response?.data || error.message
    });
  }
});

// 7. Fantasy XI Endpoint
router.post('/fantasy', async (req, res) => {
  try {
    const { team1, team2, venue, strategy = 'Balanced XI' } = req.body;
    if (!team1 || !team2 || !venue) {
      return res.status(400).json({ error: 'team1, team2, and venue are required.' });
    }

    // 1. Fetch unique players of team1 and team2 from deliveries (in the last 4 seasons to be modern)
    // To be safe and quick, find all batters and bowlers of these two teams
    const recentMatches = await Match.find({
      $or: [
        { team1: team1, team2: team2 },
        { team1: team2, team2: team1 }
      ]
    }).sort({ date: -1 }).limit(10);

    let matchIds = recentMatches.map(m => m.matchId);
    if (matchIds.length === 0) {
      // Fallback: search any matches of these teams
      const fallbackMatches = await Match.find({
        $or: [
          { team1: team1 }, { team2: team1 },
          { team1: team2 }, { team2: team2 }
        ]
      }).sort({ date: -1 }).limit(20);
      matchIds = fallbackMatches.map(m => m.matchId);
    }

    // Get list of players who played in these matches
    const playersInMatches = await Delivery.aggregate([
      { $match: { matchId: { $in: matchIds } } },
      {
        $group: {
          _id: null,
          batters: { $addToSet: '$batter' },
          bowlers: { $addToSet: '$bowler' }
        }
      }
    ]);

    let squadList = [];
    if (playersInMatches.length > 0) {
      squadList = Array.from(new Set([...playersInMatches[0].batters, ...playersInMatches[0].bowlers]));
    }
    
    // Filter out NA/Unknown
    squadList = squadList.filter(p => p && p !== 'NA' && p !== 'Unknown');

    if (squadList.length === 0) {
      // Return top 22 players historically as fallback
      const topPlayers = await Player.find().limit(25);
      squadList = topPlayers.map(p => p.name);
    }

    // 2. Fetch predicted fantasy points from FastAPI
    const pyResponse = await axios.post(`${ML_SERVICE_URL}/predict/fantasy-points`, {
      players: squadList,
      venue,
      season: '2024',
      opponent_team: team2
    });

    const predictions = pyResponse.data.predictions;

    // 3. Select Fantasy XI
    // Categorize
    const wkPool = [];
    const batPool = [];
    const arPool = [];
    const bowlPool = [];

    predictions.forEach(p => {
      if (p.role === 'Wicketkeeper') wkPool.push(p);
      else if (p.role === 'Batsman') batPool.push(p);
      else if (p.role === 'All-Rounder') arPool.push(p);
      else bowlPool.push(p);
    });

    // Sort pools by points descending
    const sortByPoints = (a, b) => b.predicted_points - a.predicted_points;
    wkPool.sort(sortByPoints);
    batPool.sort(sortByPoints);
    arPool.sort(sortByPoints);
    bowlPool.sort(sortByPoints);

    const selected = [];
    
    // Must select at least 1 WK
    if (wkPool.length > 0) {
      selected.push(wkPool[0]);
    } else {
      // Fallback
      const topFallback = predictions.sort(sortByPoints)[0];
      if (topFallback) {
        topFallback.role = 'Wicketkeeper';
        selected.push(topFallback);
      }
    }

    let batCount = 4, arCount = 2, bowlCount = 4;
    if (strategy === 'Batting-Heavy XI') {
      batCount = 5;
      arCount = 2;
      bowlCount = 3;
    } else if (strategy === 'Bowling-Heavy XI') {
      batCount = 3;
      arCount = 2;
      bowlCount = 5;
    }

    // Add Batters
    for (let i = 0; i < batCount && i < batPool.length; i++) {
      selected.push(batPool[i]);
    }
    // Add All-Rounders
    for (let i = 0; i < arCount && i < arPool.length; i++) {
      selected.push(arPool[i]);
    }
    // Add Bowlers
    for (let i = 0; i < bowlCount && i < bowlPool.length; i++) {
      selected.push(bowlPool[i]);
    }

    // Fill up to 11 if we are short
    const selectedNames = new Set(selected.map(p => p.name));
    const sortedAll = predictions.sort(sortByPoints);
    for (const p of sortedAll) {
      if (selected.length >= 11) break;
      if (!selectedNames.has(p.name)) {
        selected.push(p);
        selectedNames.add(p.name);
      }
    }

    // Assign Captain (highest points) and Vice Captain (second highest)
    selected.sort(sortByPoints);
    if (selected.length > 0) selected[0].isCaptain = true;
    if (selected.length > 1) selected[1].isViceCaptain = true;

    res.json(selected);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
