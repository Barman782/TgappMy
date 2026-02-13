# Tomb Raider King: Relic Wars — Telegram Mini App Technical Specification

## 1) Product Vision & Scope

**Game concept:** A turn-based, collectible card battler inspired by Hearthstone combat structure and pacing, with Tomb Raider King-inspired lore, relic hierarchy, tomb raids, cursed artifacts, and hunter factions.

**Primary platform:** Telegram Mini App (WebApp embedded in Telegram clients).

**Monetization platform:** Telegram Stars using Bot API invoice/payment lifecycle.

**Core modes:**
- PvP asynchronous ladder (ranked + casual)
- PvE tomb raids (boss guardians)
- Collection/deck progression (relic gacha + upgrades)

---

## 2) High-Level Architecture Diagram

```mermaid
flowchart TB
    A[Telegram Client\nMini App WebView] --> B[Next.js Frontend\nTelegram WebApp SDK]
    A --> C[Telegram Bot (aiogram)]

    B --> D[FastAPI Game API]
    C --> D
    C --> E[Telegram Bot API]

    D --> F[(PostgreSQL)]
    D --> G[(Redis)]
    D --> H[Matchmaker Worker]
    D --> I[Combat/Rules Engine Service]
    D --> J[Payment Service\nStars validation]
    D --> K[Gacha RNG Service\nseeded + auditable]
    D --> L[Notification Service]

    L --> C
    H --> G
    I --> F
    J --> F
    K --> F

    M[Admin/LiveOps Panel] --> D
    N[Analytics Pipeline\n(events, LTV, ARPU)] --> O[(Data Warehouse)]
    B --> N
    D --> N
```

### Service Responsibilities
- **Next.js Mini App:** UI, animations, deck builder UX, battle replay rendering, Telegram init data handling.
- **FastAPI Gateway:** authenticated API orchestration, anti-cheat command validation, economy operations.
- **Combat Engine:** deterministic turn resolution, card effect stack, passive triggers.
- **Matchmaker Worker:** async PvP pairing, ELO/MMR bucket queues in Redis.
- **Gacha Service:** server-authoritative summon outcomes, pity counters, anti-exploit checks.
- **Payment Service:** invoice creation + pre-checkout + successful payment fulfillment.
- **Bot (aiogram):** launch entrypoint, deep links, push notifications, referral events.

---

## 3) Gameplay Design (Hearthstone-Like, Tomb Raider King-Themed)

## 3.1 Match Rules
- Deck size: **30 cards**.
- Starting hand: 3 cards (first player), 4 cards (second player).
- Turn timer: 60s default (PvP async can use “turn window” e.g., 12h).
- Mana system:
  - Starts at 1, grows by 1 each turn to max 10.
  - Optional bonus relic effects can temporarily increase mana.
- Win condition:
  - Reduce enemy Hunter HP to 0.
  - Alternative raid objective modes for tomb boss encounters.

## 3.2 Card Types
- **Relic Cards** (core play cards; equivalent to minions/spells depending subtype)
  - Summon relic entities, cast cursed effects, trigger tomb traps.
- **Artifact Cards** (equipment)
  - Bind to hero or relic slot, grant persistent buffs.
- **Tomb Event Cards** (environment)
  - Temporary zone modifiers (sandstorm, curse fog, divine suppression).

## 3.3 Rarity & Acquisition
- Common, Rare, Epic, Legendary.
- Duplicate protection for Legendary drops (until collection completion).
- Shard conversion from duplicates for crafting target relics.

## 3.4 Turn Resolution Order
1. Start-of-turn passives (auras, ongoing curses).
2. Draw phase.
3. Main action phase (play relics/artifacts/use hero power).
4. Combat declaration and resolution.
5. End-of-turn triggers (poison, delayed tomb collapse effects).

## 3.5 Boss Raid Mechanics
- PvE tomb bosses have **phase-based HP thresholds**.
- Guardian mechanics:
  - Ancient shields (damage cap per turn)
  - Curse mark stacks (periodic unavoidable damage)
  - Summoned relic sentinels
- Weekly rotating raid mutators (e.g., “Forbidden Tomb: all Epic costs -1”).

---

## 4) Hero Classes (Tomb Raider King-inspired)

## 4.1 Relic Hunter (DPS)
- **Identity:** Aggressive artifact thief; burst and tempo.
- **Passive:** *Greedy Instinct* — first relic stolen/destroyed each match grants +1/+1 random hand relic.
- **Ultimate:** *King’s Plunder* — copy strongest enemy artifact, reduce its cost to 0 this turn.
- **Personality text/voice tone:** taunting, opportunistic, dark humor (“Everything buried belongs to me.”)

## 4.2 Support Excavator
- **Identity:** Sustain, shields, utility excavation tools.
- **Passive:** *Surveyor’s Insight* — after playing 3 support cards, discover 1 relic from top 5 deck cards.
- **Ultimate:** *Sanctum Reinforcement* — grant all allied relics Barrier + heal hero.
- **Personality tone:** calm strategist, pragmatic (“A proper dig saves lives and wins wars.”)

## 4.3 Cursed Relic User
- **Identity:** Self-damage risk for high control/value.
- **Passive:** *Hex Conduit* — whenever you take self-damage, apply 1 Curse to random enemy.
- **Ultimate:** *Pandora Unleashed* — detonate all curses; each stack deals AoE damage.
- **Personality tone:** sinister, obsessive (“The relic whispers, I obey.”)

## 4.4 Ancient Guardian
- **Identity:** Defensive scaling, anti-burst.
- **Passive:** *Eternal Stone* — first time each turn this hero takes damage, reduce by 2.
- **Ultimate:** *Tomb Sovereignty* — lock enemy highest-cost card for 2 turns, gain massive armor.
- **Personality tone:** stoic, ancient authority (“You trespass in sacred stone.”)

## 4.5 Tomb Boss (PvE Enemy Archetype)
- **Identity:** multi-phase scripted AI.
- **Passive:** *Domain Rule* — global tomb modifier active throughout encounter.
- **Ultimate:** *Relic Cataclysm* — scripted raid wipe unless objective counter-play is completed.
- **Tone:** mythic, threatening, ceremonial.

---

## 5) Core Systems

1. **Deck Builder UI**
   - Filter by class, rarity, mana, keywords.
   - Illegal deck validation server-side (30 cards, duplicate rules).
2. **Async PvP Matchmaking**
   - Turn tickets + push reminders through bot.
   - MMR buckets and anti-stall penalties.
3. **PvE Tomb Raids**
   - Solo and guild raid ladders.
   - Weekly raid boss rotation + mutators.
4. **Relic Summoning (Gacha)**
   - Banner pools (standard/event).
   - Pity thresholds and public rate table.
5. **Inventory & Upgrade**
   - Relic levels, ascension, trait reroll tokens.
6. **Leaderboard**
   - Top Hunters global/region + guild rankings.
7. **Daily Missions & Quests**
   - Dynamic objectives tied to retention loops.
8. **Relic Guilds (Clans)**
   - Guild chat hooks, shared raid progress, guild shop.

---

## 6) Telegram Bot + Mini App Integration Flow

## 6.1 Launch/Auth Flow
1. User opens bot and taps **Play** (WebApp keyboard button).
2. Telegram opens Mini App with signed `initData`.
3. Frontend sends `initData` to `/auth/telegram`.
4. Backend validates hash per Telegram WebApp auth spec.
5. Backend creates/updates player profile mapped to `telegram_user_id`.
6. Backend issues short-lived JWT + refresh token.

## 6.2 Session/Cloud Save
- Every state-changing action goes through signed API calls.
- Battle actions are command events, never trusted from client as final state.
- Server snapshot + event log allow replay and rollback.

## 6.3 Notifications
- aiogram bot sends:
  - Turn reminders
  - Energy full alerts
  - Event start/end
  - Referral reward claims

---

## 7) Shop & Telegram Stars Payment Logic

## 7.1 Product Catalog (Example)
- 100⭐ Small Relic Pack
- 500⭐ Epic Relic Chest
- 1000⭐ Legendary Hunter Skin
- 2000⭐ Battle Pass
- 150⭐ Energy Refill Bundle
- 800⭐ Premium Tomb Raid Pass

## 7.2 Payment Sequence
1. Client requests `/shop/invoice` with SKU.
2. Backend creates Telegram invoice payload (`sendInvoice`) through bot.
3. Telegram sends `pre_checkout_query` to bot.
4. Bot validates SKU, price, user lock status, nonce.
5. Bot answers pre-checkout OK.
6. Telegram sends successful payment update.
7. Backend performs idempotent fulfillment transaction:
   - verify payload signature/nonce
   - ensure not previously processed
   - grant entitlements
   - append economy ledger entry
8. Client refreshes wallet/inventory.

## 7.3 Anti-Fraud & Idempotency
- Unique `payment_tx_id` + `invoice_nonce`.
- Fulfillment in DB transaction with unique constraint on tx id.
- If duplicate callback received: no extra grant.

## 7.4 F2P / Fairness Design
- No direct sale of guaranteed ranked dominance.
- Paid items accelerate collection cosmetics/progression speed.
- Competitive fairness controls:
  - Matchmaking by power band and rank.
  - Seasonal free card track and guaranteed craft resources.

---

## 8) Security, Anti-Cheat, and Economy Integrity

- **Server-authoritative combat:** client sends intents only.
- **Deterministic RNG:** seed committed at match start; reveal strategy for audits.
- **Gacha exploit prevention:**
  - RNG on server only
  - signed result packets
  - rate-limit summon endpoints
- **Economy ledger:** append-only table for every currency mutation.
- **Abuse detection:**
  - impossible turn timings
  - repeated identical action patterns
  - suspicious payment mismatch logs
- **Scale target 100k+ users:**
  - stateless API pods + Redis queues
  - read replicas for leaderboard queries
  - CDN caching for assets/cards metadata

---

## 9) Database Schema (PostgreSQL)

```sql
-- Identity
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  telegram_user_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  display_name TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  last_login_at TIMESTAMPTZ
);

CREATE TABLE player_profiles (
  user_id BIGINT PRIMARY KEY REFERENCES users(id),
  level INT DEFAULT 1,
  exp INT DEFAULT 0,
  mmr INT DEFAULT 1000,
  rank_tier TEXT DEFAULT 'Bronze',
  energy INT DEFAULT 100,
  stars_spent_total INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Cards/Collection
CREATE TABLE relic_cards (
  id BIGSERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  rarity TEXT NOT NULL,
  class_tag TEXT,
  mana_cost INT NOT NULL,
  attack INT,
  health INT,
  effect_json JSONB NOT NULL
);

CREATE TABLE user_card_inventory (
  user_id BIGINT REFERENCES users(id),
  relic_card_id BIGINT REFERENCES relic_cards(id),
  quantity INT NOT NULL DEFAULT 0,
  foil BOOL DEFAULT FALSE,
  PRIMARY KEY(user_id, relic_card_id, foil)
);

CREATE TABLE decks (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  name TEXT NOT NULL,
  hero_class TEXT NOT NULL,
  is_active BOOL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE deck_cards (
  deck_id BIGINT REFERENCES decks(id) ON DELETE CASCADE,
  relic_card_id BIGINT REFERENCES relic_cards(id),
  qty INT NOT NULL,
  PRIMARY KEY(deck_id, relic_card_id)
);

-- Match/Combat
CREATE TABLE matches (
  id BIGSERIAL PRIMARY KEY,
  mode TEXT NOT NULL,
  player1_id BIGINT REFERENCES users(id),
  player2_id BIGINT REFERENCES users(id),
  winner_user_id BIGINT REFERENCES users(id),
  state_json JSONB NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  ended_at TIMESTAMPTZ
);

CREATE TABLE match_events (
  id BIGSERIAL PRIMARY KEY,
  match_id BIGINT REFERENCES matches(id) ON DELETE CASCADE,
  turn_no INT NOT NULL,
  actor_user_id BIGINT REFERENCES users(id),
  command_json JSONB NOT NULL,
  resolved_state_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Gacha/Economy
CREATE TABLE summon_banners (
  id BIGSERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  rates_json JSONB NOT NULL,
  pity_rule_json JSONB NOT NULL,
  starts_at TIMESTAMPTZ,
  ends_at TIMESTAMPTZ
);

CREATE TABLE summon_history (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  banner_id BIGINT REFERENCES summon_banners(id),
  result_json JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE wallets (
  user_id BIGINT PRIMARY KEY REFERENCES users(id),
  soft_currency INT DEFAULT 0,
  premium_shards INT DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE economy_ledger (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  currency_type TEXT NOT NULL,
  delta INT NOT NULL,
  reason TEXT NOT NULL,
  ref_type TEXT,
  ref_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Payments
CREATE TABLE payments (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  sku_code TEXT NOT NULL,
  stars_amount INT NOT NULL,
  telegram_payment_charge_id TEXT UNIQUE,
  provider_payment_charge_id TEXT,
  invoice_payload TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  confirmed_at TIMESTAMPTZ
);

-- Social/Guild
CREATE TABLE guilds (
  id BIGSERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  owner_user_id BIGINT REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE guild_members (
  guild_id BIGINT REFERENCES guilds(id) ON DELETE CASCADE,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  joined_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY(guild_id, user_id)
);
```

---

## 10) Production Folder Structure

```text
relic-wars/
  apps/
    miniapp-web/                 # Next.js + Telegram WebApp SDK
      src/
        app/
        components/
        features/
          auth/
          deck-builder/
          battle/
          shop/
          raids/
          guilds/
        lib/
          telegram.ts
          api-client.ts
    bot-service/                 # aiogram bot
      bot/
        handlers/
        middlewares/
        keyboards/
        services/
      main.py
    game-api/                    # FastAPI backend
      app/
        api/
          v1/
            auth.py
            decks.py
            battle.py
            matchmaking.py
            summon.py
            shop.py
            guilds.py
        core/
          config.py
          security.py
          redis.py
        domain/
          combat_engine/
          economy/
          gacha/
          matchmaking/
        db/
          models/
          migrations/
          repositories/
        workers/
          matchmaking_worker.py
          notifications_worker.py
  packages/
    shared-schema/               # card/effect contracts
    shared-types/
  infra/
    docker/
    k8s/
    terraform/
  docs/
    GAME_DESIGN.md
    TECHNICAL_SPEC.md
```

---

## 11) Example Code Snippets

## 11.1 Frontend (Next.js Telegram auth bootstrap)

```ts
// apps/miniapp-web/src/lib/telegram.ts
export function getTelegramInitData(): string {
  const w = window as any;
  if (!w.Telegram?.WebApp) throw new Error("Telegram WebApp SDK unavailable");
  w.Telegram.WebApp.ready();
  return w.Telegram.WebApp.initData || "";
}
```

```ts
// apps/miniapp-web/src/features/auth/useTelegramAuth.ts
import { useEffect } from "react";
import { getTelegramInitData } from "@/lib/telegram";

export function useTelegramAuth() {
  useEffect(() => {
    (async () => {
      const initData = getTelegramInitData();
      const res = await fetch("/api/auth/telegram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ initData })
      });
      if (!res.ok) throw new Error("Telegram auth failed");
    })();
  }, []);
}
```

## 11.2 FastAPI Telegram initData validation

```python
# apps/game-api/app/api/v1/auth.py
import hmac
import hashlib
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/auth/telegram")
def auth_telegram(payload: dict):
    init_data = payload.get("initData", "")
    if not verify_init_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram signature")
    # parse user, upsert profile, issue JWT
    return {"ok": True}


def verify_init_data(init_data: str) -> bool:
    # Pseudocode: implement exactly as Telegram docs define.
    bot_token = "<BOT_TOKEN>"
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    # build data_check_string and compare with constant-time equality
    return True
```

## 11.3 aiogram payment handler (Telegram Stars)

```python
# apps/bot-service/bot/handlers/payments.py
from aiogram import Router, F
from aiogram.types import PreCheckoutQuery, Message

router = Router()

@router.pre_checkout_query()
async def pre_checkout(pcq: PreCheckoutQuery, bot):
    # validate payload/sku/user status
    await bot.answer_pre_checkout_query(pcq.id, ok=True)

@router.message(F.successful_payment)
async def on_successful_payment(message: Message):
    payment = message.successful_payment
    # call game-api fulfillment endpoint (idempotent)
    # persist tx and grant purchased goods
```

## 11.4 Gacha summon endpoint (server-authoritative)

```python
# apps/game-api/app/api/v1/summon.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/summon/{banner_code}")
def summon(banner_code: str, user=Depends(get_user)):
    # 1) load active banner
    # 2) apply pity counter
    # 3) generate result on server RNG
    # 4) write summon_history + inventory + ledger in one transaction
    return {
        "banner": banner_code,
        "results": ["RELIC_LEGEND_007"],
        "pity": {"legendary_in": 21}
    }
```

---

## 12) Retention & Viral Systems

- **Daily login streak** with escalating rewards (day 7 guaranteed Rare+).
- **Referral system:** deep-link invite via bot `/start ref_<id>`; both users receive rewards after milestone.
- **Limited-time relic events:** exclusive banners and raid bosses.
- **Ranked seasons:** monthly reset + end-season cosmetics.
- **Global leaderboard:** in-app + bot command snapshots.

---

## 13) Monetization Economy Model (LTV/ARPU Logic)

## 13.1 Economy Pillars
- Strong F2P core loop: daily quests + craft system + pity.
- Monetization centered on:
  - convenience (energy/refills)
  - cosmetics (skins, VFX)
  - broad progression acceleration (packs/pass)
- Preserve fairness in competitive modes.

## 13.2 Example KPI Targets
- D1 retention: 40%+
- D7 retention: 18%+
- D30 retention: 8%+
- Payer conversion: 2.5–4%
- ARPPU monthly: 18–35 USD equivalent in Stars

## 13.3 Simple Revenue Model
- `ARPU = Total Revenue / MAU`
- `LTV ≈ ARPDAU × Avg Lifetime Days`
- Segment assumptions:
  - Minnows buy Small Packs/Battle Pass.
  - Dolphins buy event bundles + raid passes.
  - Whales focus cosmetics completion + high-frequency gacha.

## 13.4 LiveOps Cadence
- Weekly: event banner + raid modifier.
- Biweekly: balance patch and new relic package.
- Monthly: ranked season + battle pass reset.
- Quarterly: major feature drop (new class/guild raid tier).

---

## 14) Scalability Plan (100k+ users)

- Horizontal autoscaling for API pods.
- Redis streams/queues for asynchronous game events.
- Read-heavy endpoints cached (leaderboards/cards catalog).
- Postgres partitioning for `match_events` and `economy_ledger`.
- Observability stack:
  - OpenTelemetry traces
  - Prometheus/Grafana metrics
  - Alerting for payment failures and queue lag

---

## 15) MVP Roadmap

### Phase 1 (8–10 weeks)
- Telegram auth + profile + deck builder
- Core PvP async combat (1 class)
- Shop with Stars + 3 SKUs
- Basic gacha + inventory

### Phase 2 (6–8 weeks)
- 3 additional classes
- PvE raids + guild basics
- Battle pass + daily quests

### Phase 3 (ongoing live ops)
- Seasonal events, clan wars, advanced cosmetics
- anti-cheat anomaly scoring and economy tuning

