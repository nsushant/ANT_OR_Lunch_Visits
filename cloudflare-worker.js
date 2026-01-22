/**
 * Cloudflare Worker for Lunch Votes
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to https://workers.cloudflare.com/ and sign up (free)
 * 2. Create a new Worker
 * 3. Paste this code
 * 4. Add your GitHub token as an environment variable:
 *    - Go to Settings > Variables
 *    - Add: GITHUB_TOKEN = ghp_yourActualToken
 * 5. Deploy and copy your worker URL (e.g., https://lunch-votes.yourname.workers.dev)
 * 6. Update the WORKER_URL in lunch_map.html and ranking.html
 */

const GITHUB_OWNER = 'nsushant';
const GITHUB_REPO = 'ANT_OR_Lunch_Visits';
const VOTES_FILE = 'votes.json';

// Allowed origins (update with your GitHub Pages URL)
const ALLOWED_ORIGINS = [
  'https://nsushant.github.io',
  'http://localhost:5500',  // For local testing
  'http://127.0.0.1:5500',
  'null' // For file:// protocol
];

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const isAllowed = ALLOWED_ORIGINS.includes(origin) || origin === '';
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': isAllowed ? origin || '*' : ALLOWED_ORIGINS[0],
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // GET - fetch current votes
    if (request.method === 'GET') {
      try {
        const response = await fetch(
          `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/main/${VOTES_FILE}?t=${Date.now()}`
        );
        const data = await response.json();
        return new Response(JSON.stringify(data), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: 'Failed to fetch votes' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // POST - update votes
    if (request.method === 'POST') {
      try {
        const { votes, user } = await request.json();
        
        if (!votes || typeof votes !== 'object') {
          return new Response(JSON.stringify({ error: 'Invalid votes data' }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Get GitHub token from environment variable (secure!)
        const GITHUB_TOKEN = env.GITHUB_TOKEN;
        if (!GITHUB_TOKEN) {
          return new Response(JSON.stringify({ error: 'Server not configured' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        // Get current file SHA
        const fileRes = await fetch(
          `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${VOTES_FILE}`,
          {
            headers: {
              'Authorization': `token ${GITHUB_TOKEN}`,
              'User-Agent': 'LunchVotes-Worker'
            }
          }
        );
        
        if (!fileRes.ok) {
          const err = await fileRes.json();
          return new Response(JSON.stringify({ error: 'Failed to get file: ' + err.message }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }
        
        const fileData = await fileRes.json();

        // Prepare new content
        const newContent = JSON.stringify({
          votes: votes,
          lastUpdated: new Date().toISOString()
        }, null, 2);

        // Update file
        const updateRes = await fetch(
          `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${VOTES_FILE}`,
          {
            method: 'PUT',
            headers: {
              'Authorization': `token ${GITHUB_TOKEN}`,
              'Content-Type': 'application/json',
              'User-Agent': 'LunchVotes-Worker'
            },
            body: JSON.stringify({
              message: `Vote update by ${user || 'Anonymous'}`,
              content: btoa(newContent),
              sha: fileData.sha
            })
          }
        );

        if (!updateRes.ok) {
          const err = await updateRes.json();
          return new Response(JSON.stringify({ error: 'Failed to update: ' + err.message }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

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
