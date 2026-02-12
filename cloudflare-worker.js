/**
 * Cloudflare Worker for Lunch Votes
 * 
 * Features:
 * - D1 database for vote storage
 * - Turnstile captcha verification
 * - 10 votes per user per day limit
 * 
 * SETUP:
 * 1. Create D1 database and table (see CLOUDFLARE_D1_TURNSTILE_SETUP.md)
 * 2. Add D1 binding: DB = lunch-votes
 * 3. Add variable: TURNSTILE_SECRET_KEY = your-secret-key
 */

const ALLOWED_ORIGINS = [
  'https://nsushant.github.io',
  'http://localhost:5500',
  'http://127.0.0.1:5500',
  'null'
];

const VOTES_PER_USER_PER_DAY = 10;

// Get D1 database - try multiple possible binding names
function getDB(env) {
  return env.DB || env.Lunch_votes || env['Lunch-votes'] || null;
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const isAllowed = ALLOWED_ORIGINS.includes(origin) || origin === '';
    
    const corsHeaders = {
      'Access-Control-Allow-Origin': isAllowed ? origin || '*' : ALLOWED_ORIGINS[0],
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // GET - fetch all votes
    if (request.method === 'GET') {
      try {
        const db = getDB(env);
        if (!db) {
          return new Response(JSON.stringify({ error: 'Database not configured' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        const result = await db.prepare(
          'SELECT restaurant_name, user_name, rank, created_at FROM votes ORDER BY created_at DESC'
        ).all();

        // Transform to the format expected by frontend
        const votes = {};
        for (const row of result.results) {
          if (!votes[row.restaurant_name]) {
            votes[row.restaurant_name] = {};
          }
          votes[row.restaurant_name][row.user_name] = row.rank;
        }

        return new Response(JSON.stringify({ votes }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: 'Failed to fetch votes: ' + error.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // POST - submit a vote
    if (request.method === 'POST') {
      try {
        const db = getDB(env);
        if (!db) {
          return new Response(JSON.stringify({ error: 'Database not configured' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        const { restaurant_name, user_name, rank, turnstile_token } = await request.json();

        // Validate required fields
        if (!restaurant_name || !user_name || !rank) {
          return new Response(JSON.stringify({ error: 'Missing required fields' }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Validate rank
        if (![1, 2, 3].includes(rank)) {
          return new Response(JSON.stringify({ error: 'Rank must be 1, 2, or 3' }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Verify Turnstile token
        if (!env.TURNSTILE_SECRET_KEY) {
          return new Response(JSON.stringify({ error: 'Turnstile not configured' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        const ip = request.headers.get('CF-Connecting-IP');
        const turnstileResult = await verifyTurnstile(env.TURNSTILE_SECRET_KEY, turnstile_token, ip);
        
        if (!turnstileResult.success) {
          return new Response(JSON.stringify({ error: 'Captcha verification failed' }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Check user's vote count today
        const today = new Date().toISOString().split('T')[0];
        const voteCountResult = await db.prepare(
          `SELECT COUNT(*) as count FROM votes WHERE user_name = ? AND date(created_at) = ?`
        ).bind(user_name, today).first();

        const currentVoteCount = voteCountResult?.count || 0;

        if (currentVoteCount >= VOTES_PER_USER_PER_DAY) {
          return new Response(JSON.stringify({ 
            error: `Daily vote limit reached. You can vote ${VOTES_PER_USER_PER_DAY} times per day.` 
          }), {
            status: 429,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Check if user already voted for this restaurant
        const existingVote = await db.prepare(
          'SELECT rank FROM votes WHERE restaurant_name = ? AND user_name = ?'
        ).bind(restaurant_name, user_name).first();

        if (existingVote) {
          return new Response(JSON.stringify({ 
            error: `You already voted for ${restaurant_name} with rank ${existingVote.rank}` 
          }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Check if user already used this rank for ANY restaurant today
        const rankUsed = await db.prepare(
          `SELECT restaurant_name FROM votes WHERE user_name = ? AND rank = ? AND date(created_at) = ?`
        ).bind(user_name, rank, today).first();

        if (rankUsed) {
          return new Response(JSON.stringify({ 
            error: `You already used rank ${rank} for ${rankUsed.restaurant_name}. Each rank can only be used once per day.` 
          }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Insert the vote
        await db.prepare(
          'INSERT INTO votes (restaurant_name, user_name, rank) VALUES (?, ?, ?)'
        ).bind(restaurant_name, user_name, rank).run();

        return new Response(JSON.stringify({ 
          success: true, 
          votesRemaining: VOTES_PER_USER_PER_DAY - currentVoteCount - 1 
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // DELETE - reset all votes (admin only)
    if (request.method === 'DELETE') {
      try {
        const db = getDB(env);
        if (!db) {
          return new Response(JSON.stringify({ error: 'Database not configured' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        const { admin_key } = await request.json();
        
        // Simple admin key check (set in Cloudflare variables)
        if (admin_key !== env.ADMIN_KEY) {
          return new Response(JSON.stringify({ error: 'Unauthorized' }), {
            status: 401,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        await db.prepare('DELETE FROM votes').run();

        return new Response(JSON.stringify({ success: true }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    return new Response('Method not allowed', { 
      status: 405, 
      headers: corsHeaders 
    });
  }
};

async function verifyTurnstile(secretKey, token, remoteip) {
  const formData = new FormData();
  formData.append('secret', secretKey);
  formData.append('response', token);
  if (remoteip) {
    formData.append('remoteip', remoteip);
  }

  const result = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    body: formData
  });

  return await result.json();
}
