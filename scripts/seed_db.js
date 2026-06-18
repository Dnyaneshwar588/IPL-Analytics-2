const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const mongoose = require('mongoose');
const Match = require('../backend/models/match.model');
const Delivery = require('../backend/models/delivery.model');
const Team = require('../backend/models/team.model');
const Player = require('../backend/models/player.model');

require('dotenv').config({ path: path.join(__dirname, '../backend/.env') });

const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/ipl_analytics';

const TEAM_MAPPING = {
  'Delhi Daredevils': 'Delhi Capitals',
  'Kings XI Punjab': 'Punjab Kings',
  'Deccan Chargers': 'Sunrisers Hyderabad',
  'Rising Pune Supergiants': 'Rising Pune Supergiant',
  'Rising Pune Supergiant': 'Rising Pune Supergiant',
  'Pune Warriors': 'Pune Warriors'
};

function normalizeTeam(team) {
  if (!team) return 'Unknown';
  const trimmed = team.trim();
  return TEAM_MAPPING[trimmed] || trimmed;
}

const VALID_WICKET_KINDS = new Set([
  'bowled',
  'caught',
  'lbw',
  'stumped',
  'caught and bowled',
  'hit wicket'
]);

const FAMOUS_WKS = new Set([
  "ms dhoni", "kd karthik", "ab de villiers", "rr pant", "kl rahul", "sv samson",
  "q de kock", "jc buttler", "wp saha", "ac gilchrist", "kc sangakkara",
  "rv uthappa", "pa patel", "dinesh karthik", "rishabh pant", "sanju samson",
  "quinton de kock", "jos buttler", "wriddhiman saha", "kumar sangakkara",
  "robin uthappa", "parthiv patel", "ishan kishan", "lh ferguson",
  "n pooran", "nicholas pooran", "ks bharat", "j bairstow", "jonny bairstow"
]);

async function seed() {
  try {
    console.log('Connecting to MongoDB...');
    await mongoose.connect(MONGO_URI);
    console.log('Connected to MongoDB successfully!');

    // Clear existing data
    console.log('Clearing existing database collections...');
    await Match.deleteMany({});
    await Delivery.deleteMany({});
    await Team.deleteMany({});
    await Player.deleteMany({});
    console.log('Collections cleared.');

    // 1. Load and Seed Matches
    const matchesPath = path.join(__dirname, '../dataset/matches.csv');
    console.log(`Parsing matches from ${matchesPath}...`);
    const matches = [];

    await new Promise((resolve, reject) => {
      fs.createReadStream(matchesPath)
        .pipe(csv())
        .on('data', (row) => {
          // Normalize names
          const team1 = normalizeTeam(row.team1);
          const team2 = normalizeTeam(row.team2);
          const winner = normalizeTeam(row.winner);
          const tossWinner = normalizeTeam(row.toss_winner);

          // Parse season to be the year (first part of split, e.g. "2007/08" -> "2007")
          let season = row.season || '';
          if (season.includes('/')) {
            season = season.split('/')[0];
          }

          matches.push({
            matchId: parseInt(row.id),
            season: season.trim(),
            city: row.city || 'Unknown',
            date: row.date ? new Date(row.date) : new Date(),
            matchType: row.match_type || 'League',
            playerOfMatch: row.player_of_match || 'Unknown',
            venue: row.venue || 'Unknown',
            team1,
            team2,
            tossWinner,
            tossDecision: row.toss_decision || 'Unknown',
            winner: row.winner === 'NA' || !row.winner ? 'No Result' : winner,
            result: row.result || 'Unknown',
            resultMargin: row.result_margin ? parseInt(row.result_margin) : 0,
            targetRuns: row.target_runs ? parseInt(row.target_runs) : 0,
            targetOvers: row.target_overs ? parseFloat(row.target_overs) : 20,
            superOver: row.super_over || 'N',
            method: row.method || 'NA',
            umpire1: row.umpire1 || 'NA',
            umpire2: row.umpire2 || 'NA'
          });
        })
        .on('end', resolve)
        .on('error', reject);
    });

    console.log(`Parsed ${matches.length} matches. Inserting into MongoDB...`);
    await Match.insertMany(matches);
    console.log('Matches seeded successfully.');

    // 2. Load and Seed Deliveries in Batches
    const deliveriesPath = path.join(__dirname, '../dataset/deliveries.csv');
    console.log(`Parsing deliveries from ${deliveriesPath}...`);
    
    // Aggregation maps to build team and player stats on the fly
    const teamStats = {};
    const playerStats = {};

    // Helper to get or init team stats
    const getTeamObj = (name) => {
      if (!teamStats[name]) {
        teamStats[name] = {
          name,
          matchesPlayed: 0,
          wins: 0,
          winPercentage: 0,
          tossWins: 0,
          tossMatchWins: 0,
          battingFirstWins: 0,
          chasingWins: 0,
          seasonStatsMap: {} // temporary map for merging
        };
      }
      return teamStats[name];
    };

    // Helper to get or init player stats
    const getPlayerObj = (name) => {
      if (!playerStats[name]) {
        playerStats[name] = {
          name,
          roles: [],
          battingStats: { runs: 0, balls: 0, dismissals: 0, average: 0, strikeRate: 0, fours: 0, sixes: 0 },
          bowlingStats: { balls: 0, runsConceded: 0, wickets: 0, economy: 0, average: 0 },
          fieldingStats: { catches: 0, stumpings: 0, runOuts: 0 },
          fantasyPoints: 0
        };
      }
      return playerStats[name];
    };

    // Calculate Team stats from matches
    console.log('Aggregating team statistics from matches...');
    for (const match of matches) {
      const t1 = getTeamObj(match.team1);
      const t2 = getTeamObj(match.team2);
      
      t1.matchesPlayed++;
      t2.matchesPlayed++;

      // Toss
      if (match.tossWinner === match.team1) {
        t1.tossWins++;
      } else if (match.tossWinner === match.team2) {
        t2.tossWins++;
      }

      // Winner
      if (match.winner && match.winner !== 'No Result') {
        const w = getTeamObj(match.winner);
        w.wins++;

        if (match.winner === match.tossWinner) {
          w.tossMatchWins++;
        }

        // Determine Batting First vs Chasing
        // tossDecision = bat -> tossWinner bats first, other fields
        // tossDecision = field -> tossWinner fields first (chases), other bats first
        const batFirst = match.tossDecision === 'bat' ? match.tossWinner : (match.tossWinner === match.team1 ? match.team2 : match.team1);
        if (match.winner === batFirst) {
          w.battingFirstWins++;
        } else {
          w.chasingWins++;
        }
      }

      // Season stats
      const s = match.season;
      if (s) {
        if (!t1.seasonStatsMap[s]) t1.seasonStatsMap[s] = { season: s, matchesPlayed: 0, wins: 0 };
        if (!t2.seasonStatsMap[s]) t2.seasonStatsMap[s] = { season: s, matchesPlayed: 0, wins: 0 };
        
        t1.seasonStatsMap[s].matchesPlayed++;
        t2.seasonStatsMap[s].matchesPlayed++;
        
        if (match.winner && match.winner !== 'No Result') {
          const w = getTeamObj(match.winner);
          if (!w.seasonStatsMap[s]) w.seasonStatsMap[s] = { season: s, matchesPlayed: 0, wins: 0 };
          w.seasonStatsMap[s].wins++;
        }
      }
    }

    // Insert deliveries in chunks
    let deliveriesBatch = [];
    const BATCH_SIZE = 20000;
    let totalDeliveriesSeeded = 0;

    const processDeliveriesBatch = async (batch) => {
      const docs = batch.map(row => {
        const battingTeam = normalizeTeam(row.batting_team);
        const bowlingTeam = normalizeTeam(row.bowling_team);
        const batsmanRuns = parseInt(row.batsman_runs) || 0;
        const extraRuns = parseInt(row.extra_runs) || 0;
        const totalRuns = parseInt(row.total_runs) || 0;
        const isWicket = parseInt(row.is_wicket) || 0;

        // Player aggregations
        const batterName = row.batter;
        const bowlerName = row.bowler;
        const nonStrikerName = row.non_striker;
        const extrasType = row.extras_type || '';
        const playerDismissed = row.player_dismissed || '';
        const dismissalKind = (row.dismissal_kind || '').toLowerCase().trim();
        const fielder = row.fielder || '';

        // Batter Stats
        if (batterName && batterName !== 'NA') {
          const b = getPlayerObj(batterName);
          b.battingStats.runs += batsmanRuns;
          if (extrasType !== 'wides') {
            b.battingStats.balls++;
          }
          if (batsmanRuns === 4) b.battingStats.fours++;
          if (batsmanRuns === 6) b.battingStats.sixes++;
        }

        // Bowler Stats
        if (bowlerName && bowlerName !== 'NA') {
          const bo = getPlayerObj(bowlerName);
          if (extrasType !== 'wides' && extrasType !== 'noballs') {
            bo.bowlingStats.balls++;
          }
          if (extrasType !== 'byes' && extrasType !== 'legbyes') {
            bo.bowlingStats.runsConceded += totalRuns;
          }
          if (isWicket === 1 && VALID_WICKET_KINDS.has(dismissalKind)) {
            bo.bowlingStats.wickets++;
          }
        }

        // Fielder Stats
        if (fielder && fielder !== 'NA' && fielder !== 'Unknown') {
          const f = getPlayerObj(fielder);
          if (dismissalKind === 'caught') f.fieldingStats.catches++;
          if (dismissalKind === 'stumped') f.fieldingStats.stumpings++;
          if (dismissalKind === 'run out') f.fieldingStats.runOuts++;
        }

        // Batter Dismissals
        if (playerDismissed && playerDismissed !== 'NA') {
          const bD = getPlayerObj(playerDismissed);
          bD.battingStats.dismissals++;
        }

        return {
          matchId: parseInt(row.match_id),
          inning: parseInt(row.inning),
          battingTeam,
          bowlingTeam,
          over: parseInt(row.over),
          ball: parseInt(row.ball),
          batter: batterName,
          bowler: bowlerName,
          nonStriker: nonStrikerName,
          batsmanRuns,
          extraRuns,
          totalRuns,
          extrasType: row.extras_type || '',
          isWicket,
          playerDismissed: row.player_dismissed || '',
          dismissalKind: row.dismissal_kind || '',
          fielder: row.fielder || ''
        };
      });

      await Delivery.insertMany(docs);
      totalDeliveriesSeeded += docs.length;
      console.log(`Seeded ${totalDeliveriesSeeded} deliveries...`);
    };

    await new Promise((resolve, reject) => {
      fs.createReadStream(deliveriesPath)
        .pipe(csv())
        .on('data', (row) => {
          deliveriesBatch.push(row);
          if (deliveriesBatch.length >= BATCH_SIZE) {
            const currentBatch = deliveriesBatch;
            deliveriesBatch = [];
            // Pause stream while database write happens to prevent buffer overload
            parserStream.pause();
            processDeliveriesBatch(currentBatch)
              .then(() => parserStream.resume())
              .catch(err => reject(err));
          }
        })
        .on('end', async () => {
          if (deliveriesBatch.length > 0) {
            try {
              await processDeliveriesBatch(deliveriesBatch);
              resolve();
            } catch (err) {
              reject(err);
            }
          } else {
            resolve();
          }
        })
        .on('error', reject);

      const parserStream = fs.createReadStream(deliveriesPath).pipe(csv());
    });

    console.log('Deliveries seeded successfully.');

    // 3. Finalize and Save Teams
    console.log('Saving aggregated team statistics...');
    const teamsToSave = Object.values(teamStats).map(t => {
      t.winPercentage = t.matchesPlayed > 0 ? parseFloat((t.wins / t.matchesPlayed * 100).toFixed(2)) : 0;
      t.seasonStats = Object.values(t.seasonStatsMap);
      delete t.seasonStatsMap;
      return t;
    });
    await Team.insertMany(teamsToSave);
    console.log(`Saved ${teamsToSave.length} teams.`);

    // 4. Finalize and Save Players
    console.log('Calculating player averages, strike rates, and fantasy points...');
    const playersToSave = Object.values(playerStats).map(p => {
      // Batting Avg & Strike Rate
      const bat = p.battingStats;
      bat.average = bat.dismissals > 0 ? parseFloat((bat.runs / bat.dismissals).toFixed(2)) : bat.runs;
      bat.strikeRate = bat.balls > 0 ? parseFloat((bat.runs / bat.balls * 100).toFixed(2)) : 0;

      // Bowling Avg & Economy
      const bowl = p.bowlingStats;
      const overs = bowl.balls / 6;
      bowl.economy = overs > 0 ? parseFloat((bowl.runsConceded / overs).toFixed(2)) : 0;
      bowl.average = bowl.wickets > 0 ? parseFloat((bowl.runsConceded / bowl.wickets).toFixed(2)) : 0;

      // Determine Roles
      const lowerName = p.name.toLowerCase();
      if (FAMOUS_WKS.has(lowerName)) {
        p.roles.push('Wicketkeeper');
      }
      if (bat.runs >= 150 && bowl.wickets >= 5) {
        p.roles.push('All-Rounder');
      } else if (bowl.wickets >= 6 && (bat.runs < 100 || bowl.wickets * 22 > bat.runs)) {
        p.roles.push('Bowler');
      } else {
        p.roles.push('Batsman');
      }

      // Calculate simplified Total Fantasy Points
      // Dream11 based formula:
      // Runs: 1 pt, Wickets: 25 pt, Fours: +1 pt, Sixes: +2 pt, 30 bonus: +4 pt, 50 bonus: +8 pt, 100 bonus: +16 pt
      // Catches: 8 pt, Stumpings: 12 pt, Run outs: 6 pt
      let fp = 0;
      fp += bat.runs;
      fp += bat.fours * 1;
      fp += bat.sixes * 2;
      fp += bowl.wickets * 25;
      fp += p.fieldingStats.catches * 8;
      fp += p.fieldingStats.stumpings * 12;
      fp += p.fieldingStats.runOuts * 6;
      
      p.fantasyPoints = Math.round(fp);

      return p;
    });

    // Save players in batches to avoid MongoDB document size/payload limit
    const PLAYER_BATCH = 5000;
    for (let i = 0; i < playersToSave.length; i += PLAYER_BATCH) {
      const chunk = playersToSave.slice(i, i + PLAYER_BATCH);
      await Player.insertMany(chunk);
    }
    console.log(`Saved ${playersToSave.length} players.`);

    console.log('Database Seeding Completed Successfully!');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
}

seed();
