"""Complaint taxonomy for the MoveInSync employee app (data-only module, no logic).

Derived from reading 502 development-split reviews rated 1-3 stars in the window 2025-10-10..2026-10-09.
Each category has regex patterns (case-insensitive) matched against the normalised review text.

Pattern forms
  "regex"                      matches if the regex is found
  ("all", [regex, regex, ...]) matches only if EVERY regex is found (use for context cues)
Trick: r"^(?!.*\\bword\\b)" is true only when `word` is ABSENT (used as an exclusion inside "all").

Nature: technical | operational | usability | policy | mixed | cross-cutting
Families group categories for reporting only.
"""

NEG = (r"(?:\bnot\b|\bno\b|\bnever\b|\bunable\b|\bcan'?t\b|\bcannot\b|\bwon'?t\b|\bdoesn'?t\b|\bdon'?t\b|"
       r"\bdidn'?t\b|\bisn'?t\b|\bwasn'?t\b|\bwrong\b|\bincorrect\b|\binaccurate\b|\berror\w*|\bfail\w*|"
       r"\bissue\w*|\bproblem\w*|\bbug\w*|\bslow\b|\blate\b|\bdelay\w*|\bstuck\b|\buseless\b|\bworst\b|"
       r"\bbad\b|\bpoor\b|\bpathetic\b|\bterrible\b|\bconfus\w*|\bannoying\b|\bdisappear\w*|\bmissing\b|"
       r"\bhorrible\b|\bwaste\b|\bfrustrat\w*|\bhard\b|\bdifficult\b)")

NO_DRIVER = r"^(?!.*\bdriver\b)"
NO_OTP = r"^(?!.*\botp\b)"

CATEGORIES = [
    # ---------------------------------------------------------------- Access and session
    {"id": "LOGIN_SESSION", "family": "Access & session", "nature": "technical",
     "label": "Forced logout / repeated re-login / SSO re-authentication",
     "patterns": [
         r"\botp\s+chall?eng\w*|\bverify\s+with\s+otp\b|\blogout\'?s\s+from\b",
         r"\b(?:log(?:s|ged|ging)?|sign(?:s|ed|ing)?)\s*(?:me\s+|you\s+|us\s+)?(?:out|off)\b(?!\s*(?:trip|cab|time|shift|booking|schedule|ride))",
         r"\blog-?out\s+(?:automatically|again|frequently|every|often|daily|itself)\b",
         r"\bauto(?:matic(?:ally)?)?[\s-]*(?:log|sign)[\s-]*(?:out|off)\b",
         r"\b(?:every|each)\s*(?:and\s+every\s+)?(?:time|day)\b\W+(?:\w+\W+){0,8}(?:log\s*in|login|sign\s*in)\b",
         r"\b(?:log\s*in|login|sign\s*in)\b\W+(?:\w+\W+){0,8}(?:every|each)\s*(?:and\s+every\s+)?(?:time|day)\b",
         r"\b(?:asks?|asking|requires?|required|requesting|prompts?)\s+(?:me\s+)?(?:to\s+|for\s+)?(?:re-?\s*)?(?:log\s*in|login|sign\s*in)\b",
         r"\bre-?\s*(?:login|log\s*in|sign\s*in)\b",
         r"\bvalidate\s+identity\b", r"\bsso\b", r"\bauthentication\s+app\b",
         r"\bneed\s+to\s+login\b", r"\bkeep\s+(?:us\s+|me\s+)?(?:logged|signed)\b", r"\bsigned\s+in\s+by\s+default\b",
         r"\bsave\s+login\b|\bfingerprint\b|\bbiometric\b",
         r"\b(?:many|too\s+many|so\s+many|multiple)\s+otps?\b",
         ("all", [r"\b(?:every|each)\s*time\b\W+(?:\w+\W+){0,8}\botp\b|\botp\b\W+(?:\w+\W+){0,6}(?:every|each)\s*time\b", NO_DRIVER]),
     ]},
    {"id": "ACCESS_OTP", "family": "Access & session", "nature": "technical",
     "label": "Cannot sign in / register (OTP not received or delayed)",
     "patterns": [
         r"\b(?:will|would)\s+not\s+(?:log\s*in|login)\b|\blogin\b\W+(?:\w+\W+){0,8}time-?\s*out\b",
         r"\botps?\b\W+(?:\w+\W+){0,6}(?:not|never|n't|no)\W+(?:\w+\W+){0,2}(?:receiv\w*|get\w*|com\w*|send\w*|sent|generat\w*|arriv\w*|deliver\w*)",
         r"(?:\bnot\b|\bnever\b|n't|\bno\b|\bunable\s+to\b|\bdidn'?t\b)\W+(?:\w+\W+){0,3}(?:receiv\w*|get\w*|got|send\w*|generat\w*)\W+(?:\w+\W+){0,3}\botps?\b",
         r"\botps?\b\W+(?:\w+\W+){0,3}(?:delay\w*|late\b|expired|takes?\b|took\b)",
         r"\bno\s+otps?\b|\botps?\s+function\s+down\b|\bit\s+took\s+time\s+for\s+generating\s+otp",
         r"(?:\bunable\b|\bnot\s+able\b|\bcan'?t\b|\bcannot\b|\bcouldn'?t\b|\bfail\w*)\W+(?:\w+\W+){0,2}(?:to\s+)?(?:sign[\s-]?up|register|registration|log\s*in|login|sign\s*in|verify)",
         r"\bnot\s+(?:verifying|registered)\b|\bregister\s+option\b|\bsend\s+otp\b",
     ]},
    {"id": "INSTALL_ERROR", "family": "Access & session", "nature": "technical",
     "label": "'Not installed from Play Store' error / needs uninstall-reinstall",
     "patterns": [
         r"\bnot\s+(?:been\s+)?(?:installed|downloaded)\b",
         r"\b(?:install\w*|download\w*)\s+(?:\w+\s+){0,4}from\s+(?:the\s+)?(?:play\s*store|app\s*store|google\s+play)",
         r"\bplay\s*store\b\W+(?:\w+\W+){0,6}(?:install|download|fake)",
         r"\bun-?install\w*\b\W+(?:\w+\W+){0,12}\bre-?\s*install\w*",
         r"\bre-?\s*install\w*", r"\bkeeps?\s+uninstalling\b|\bneed\s+to\s+(?:un)?install\b",
         r"\bshows?\s+(?:the\s+)?install\b|\bissues?\s+with\s+installation\b|\bfacing\s+issues?\s+with\s+install",
     ]},
    # ---------------------------------------------------------------- Stability and performance
    {"id": "CRASH_LOAD_PERF", "family": "Stability & performance", "nature": "technical",
     "label": "Crashes, blank screen, not opening, slow or endless loading",
     "patterns": [
         r"\bnever\s+works?\b|\bnot\s+stable\b|\b(?:app|application)\s+(?:is\s+)?down\b|\btime-?\s*out\b|\bstability\b|\bno\s+internet\b|\bnothing\s+without\s+internet\b",
         r"\bcrash\w*", r"\b(?:hang|hangs|hanging|hanged|freez\w*|froze)\b", r"\bblank\s+screen\b",
         r"\b(?:not|n't|never|unable\s+to|won'?t|doesn'?t|can'?t)\W+(?:\w+\W+){0,2}(?:open\w*|load\w*|start\w*|launch\w*)\b",
         r"\b(?:keeps?|continuously|always|still)\s+loading\b|\bloading\s+(?:forever|continuously|issue)",
         r"\bslow\w*\b", r"\blag\w*\b|\blatency\b",
         r"\btak(?:es|ing)\s+(?:a\s+)?(?:lot\s+of\s+|too\s+much\s+|so\s+much\s+|long\s+)?(?:time|forever|eternity|ages)\b\W+(?:\w+\W+){0,3}(?:load|open|reload)",
         r"\bcloses?\s+(?:itself|automatically|as\s+soon)\b|\bopen\s+and\s+close\b|\bnot\s+open\b",
         r"\bsomething\s+went\s+wrong\b", r"\b(?:buggy|bugs?|glitch\w*|technical\s+(?:error|issue|glitch))\b",
         r"\bserver\s+down\b|\bgoes\s+down\b", r"\bnot\s+working\b|\bdoes(?:n'?t|\s+not)\s+(?:work|function)\b|\bnot\s+able\s+to\s+access\b",
         r"\bunresponsive\b|\btoo\s+much\s+time\s+to\s+load\b",
     ]},
    {"id": "DEVICE_COMPAT", "family": "Stability & performance", "nature": "technical",
     "label": "Device / OS specific failures",
     "patterns": [r"\bpixel\b|\bandroid\s*\d+|\bhuawei\b|\boneplus\b|\bsamsung\b|\bredmi\b|\brealme\b|\bxiaomi\b|\bvivo\b|\boppo\b|\bnot\s+(?:supported|compatible)\b|\bcompatib\w*"]},
    # ---------------------------------------------------------------- Trip information accuracy
    {"id": "TRACKING_LOCATION", "family": "Trip information", "nature": "technical",
     "label": "Live tracking / GPS / map location wrong, stale or stuck",
     "patterns": [
         r"\bzoom\w*\b",
         ("all", [r"\b(?:live|real[\s-]?time)\s*(?:location|tracking|track|map|update\w*)\b|\btrack(?:ing|er|ed)?\b|\bgps\b|\bmaps?\b|\bmapping\b", NEG]),
         r"\b(?:cab|driver|vehicle|shuttle|bus|pickup|pick\s*up|drop)\s*(?:'s\s*)?location\b\W+(?:\w+\W+){0,5}(?:not|never|wrong|incorrect|inaccurate|stuck|updat\w*|ago|differ\w*)",
         r"\blocation\b\W+(?:\w+\W+){0,5}(?:not\s+(?:accurate|updat\w*|correct|show\w*|visible)|never|wrong|incorrect|inaccurate|stuck|ago|different)",
         r"\b(?:wrong|incorrect|inaccurate|different|stale)\s+(?:location|locations|destination)\b",
         r"\b(?:not|never)\s+(?:updat\w*|show\w*)\W+(?:\w+\W+){0,3}(?:location|vehicle|cab)\b",
         r"\bsuddenly\s+shows?\s+up\b|\bcab\s+tracker\b",
     ]},
    {"id": "ETA_PICKUP_TIME", "family": "Trip information", "nature": "mixed",
     "label": "ETA / pickup time inaccurate, changing, missing or unreasonably early",
     "patterns": [
         r"\b(?:exact|correct|proper|real)\s+(?:time|timings?)\b|\bpick\s*up\s+time\s+(?:varies|vary|differs?)\b|\bto\s+early\s+pick|\ballocates?\s+(?:the\s+)?trip\s+early\b|\btime\s+of\s+ride\b",
         r"\beta\b|\bestimated\s+(?:time|arrival)\b|\btime\s+estimation\b",
         ("all", [r"\b(?:pick\s*up|pickup|drop|arrival|cab|reporting)\s+(?:time|timing|timings)\b", NEG]),
         r"\btimings?\b\W+(?:\w+\W+){0,6}(?:chang\w*|wrong|incorrect|inaccurate|differ\w*|else)\b",
         r"\b(?:time|timings?)\s+(?:keeps?\s+)?chang\w*|\bchang\w*\s+(?:the\s+)?(?:pickup|pick\s*up|cab)\s+(?:time|timing)",
         r"\bwhere\s+is\s+the\s+pick\s*up\s+time\b|\bdriver\s+arrival\b|\bnot\s+(?:getting|showing)\s+pick\s*up\s+time",
         r"\b(?:pick\s*up|pickup|cab)\b\W+(?:\w+\W+){0,4}too\s+early\b|\bwhy\s+pick\s*up\s+time\s+too\b",
         r"\bpickup\s+timings?\b",
     ]},
    {"id": "NOTIFICATIONS", "family": "Trip information", "nature": "technical",
     "label": "Notifications / pop-ups: too many, wrong, delayed or missing",
     "patterns": [
         r"\bnotif\w*", r"\bpop[\s-]?ups?\b|\bbanner\b|\balerts?\b|\breminder\w*",
         r"\b(?:text\s+)?messages?\b\W+(?:\w+\W+){0,6}(?:not\b|late\b|wrong\w*|never|delay\w*|before|comes?)",
         r"\bno\s+(?:text\s+)?(?:message|sms)\b",
         ("all", [r"\bsms\b", NO_OTP]),
     ]},
    # ---------------------------------------------------------------- Booking and changes
    {"id": "BOOKING_FAILURE", "family": "Booking & changes", "nature": "mixed",
     "label": "Cannot book/schedule; bookings or schedules missing, wrong or not visible",
     "patterns": [
         r"\b(?:booked|booking)\s+(?:trip|schedules?|bookings?)\b\W+(?:\w+\W+){0,6}(?:not\s+(?:being\s+)?(?:listed|available)|empty)\b|\b(?:trip|booking)\s+(?:information|details)\s+(?:is\s+)?not\s+available\b|\bdi\s+makpag\s+book\b|\bnot\s+being\s+listed\b",
         r"\b(?:unable|not\s+able|can'?t|cannot|couldn'?t|won'?t|doesn'?t|does\s+not|not\s+allow\w*|didn'?t)\b\W+(?:\w+\W+){0,4}(?:book\w*|schedul\w*|roster\w*)\b",
         r"\b(?:book\w*|schedul\w*|roster\w*|seat)\b\W+(?:\w+\W+){0,6}(?:not\s+(?:show\w*|reflect\w*|visible|updat\w*|work\w*|get\w*)|disappear\w*|missing|fail\w*|error\w*|wrong|different\s+dates?|duplicate|stuck|freez\w*|disabled?)",
         r"\bbook\s+now\s+button\b|\bplus\s+button\b|\bwrong\s+dates?\b|\bdifferent\s+dates?\b",
         r"\b(?:future|upcoming|old|past|monthly|whole\s+month)\s+(?:booking|bookings|schedule|schedules|trips?|view)\b",
         r"\b(?:not|n't|never)\s+(?:able\s+to\s+)?(?:see|view|show\w*|get\w*)\W+(?:\w+\W+){0,4}(?:booked|schedule\w*|upcoming|trips?|booking\w*|history)\b",
         r"\b(?:trip\s+history|old\s+trips?)\b",
         r"\bbooking\s+status\b|\bbooked\s+schedules?\b",
         r"\b(?:too\s+many\s+people|all\s+seats?\s+(?:will\s+be\s+)?booked|booked\s+seats?)\b",
     ]},
    {"id": "BOOKING_RULES", "family": "Booking & changes", "nature": "policy",
     "label": "Booking window, cut-off, waitlist and transport-policy rules",
     "patterns": [
         r"\bcut[\s-]?off\b", r"\bwait[\s-]?list\w*",
         r"\b(?:\d+|one|two|three|four|eight|twelve|forty[\s-]?eight)[\s-]*(?:hours?|hrs?)\b\W+(?:\w+\W+){0,3}(?:before|prior|in\s+advance|advance)",
         r"\b(?:in\s+advance|inadvance|advance\s+booking|prior\s+booking)\b",
         r"\b(?:more|longer)\s+(?:then|than)\s+(?:1|one)\s+week\b|\bonly\s+(?:one|1)\s+day\b",
         r"\b(?:book|booking)\w*\b\W+(?:\w+\W+){0,6}(?:\d+|eight|twelve)\s*(?:hours?|hrs?|days?)\b",
         r"\b(?:visibility\s+on\s+the\s+)?polic(?:y|ies)\b\W+(?:\w+\W+){0,4}(?:visib\w*|unclear)",
     ]},
    {"id": "CANCEL_EDIT", "family": "Booking & changes", "nature": "mixed",
     "label": "Cannot cancel/edit; cancellation not honoured",
     "patterns": [
         r"\b(?:modify|amend\w*)\b\W+(?:\w+\W+){0,3}(?:booking|trip|schedule)|\bmodify\s+the\s+booking\b|\bamendments?\b",
         ("all", [r"\bcancel\w*\b", NEG]),
         r"\b(?:no|not)\s+(?:any\s+)?option\s+(?:to|for)\s+(?:cancel|edit|change|modify)\w*",
         r"\b(?:unable|can'?t|cannot|not\s+able)\s+(?:to\s+)?(?:cancel|edit|change|modify)\w*",
         r"\bedit\s+options?\b|\bno\s+way\s+to\s+(?:cancel|edit)|\bno\s+edit\b",
         r"\bchange\s+(?:the\s+|my\s+)?(?:destination|drop\s+location)\b|\bcan'?t\s+change\s+(?:the\s+)?address\b",
     ]},
    {"id": "ADDRESS_LOCATION_MGMT", "family": "Booking & changes", "nature": "mixed",
     "label": "Pickup/drop address or nodal point cannot be changed or is wrong",
     "patterns": [
         r"\bnew\s+location\b|\blocation\s+wasn\'?t\s+pinned\b|\bnot\s+pinned\b",
         r"\b(?:change|edit|update|modify|set)\w*\s+(?:the\s+|my\s+|your\s+|a\s+)?(?:pick\s*up\s+|drop\s+|home\s+)?(?:address|location|destination|drop|nodal)",
         r"\bnodal\s+point\b", r"\baddress\b\W+(?:\w+\W+){0,6}(?:not|wrong|incorrect|taken|fixed)",
         r"\b(?:exact|home)\s+location\b", r"\bwrong\s+address\b",
         r"\bpick\s*up\s+location\b\W+(?:\w+\W+){0,6}(?:far|not|wrong|stupid)",
         r"\bcoordinates\b|\bwrong\s+destination\b",
     ]},
    # ---------------------------------------------------------------- Trip status and enforcement
    {"id": "NO_SHOW", "family": "Trip status", "nature": "mixed",
     "label": "No-show marking / consequences disputed",
     "patterns": [r"\bno[\s-]?shows?\b|\bnoshow\b|\bmark\w*\s+(?:me\s+)?absent\b"]},
    {"id": "BOARDING_QR_OTP", "family": "Trip status", "nature": "technical",
     "label": "Boarding: QR scan, driver PIN/OTP, check-in",
     "patterns": [
         r"\bqr\b|\bscan(?:s|ned|ner|ning)?\b|\btorch\b|\bseat\s*(?:belt|buckle)\b|\bcheck[\s-]?in\b|\bboarding\s+(?:activit\w*|pass|issue)",
         r"\b(?:driver|pin)\b\W+(?:\w+\W+){0,6}\b(?:pin|otp)\b\W+(?:\w+\W+){0,6}(?:not|doesn'?t|work)",
         r"\bgive\s+otp\b|\botp\b\W+(?:\w+\W+){0,6}\bdriver\b|\bdriver\b\W+(?:\w+\W+){0,6}\botp\b",
     ]},
    # ---------------------------------------------------------------- Operations
    {"id": "ROUTING_ALLOCATION", "family": "Operations", "nature": "operational",
     "label": "Routing, clubbing, sequence and cab allocation",
     "patterns": [
         r"\bseater\b|\balgo(?:rithm)?\b|\bover[\s-]?(?:load|crowd)\w*\b",
         r"\brout(?:e|es|ed|ing)\b|\broutine\s+system", r"\bclub\w*\b",
         ("all", [r"\b(?:allocat\w*|allot\w*|assign\w*|rostered)\b", NEG]),
         r"\bsequence\b|\bdetours?\b|\bshorter\s+route|\blonger\s+route|\bdrop\s+(?:management|sequence|order)\b",
         r"\b(?:pick\s*up|drop)\s+(?:sequence|point)s?\b|\bnot\s+(?:allocat|assign|alott)\w*\b",
         r"\bcab\s+not\s+assign\w*\b|\bmapping\s+and\s+navigation\b|\bwhere\s+(?:are|am)\s+i\s+(?:going|being\s+dropped)\b",
     ]},
    {"id": "VEHICLE_DRIVER_OPS", "family": "Operations", "nature": "operational",
     "label": "Cab late/not provided, driver conduct, vendor / transport-team failures",
     "patterns": [
         r"\b(?:always|everyday|every\s+day|daily)\s+(?:\w+\s+){0,4}late\b|\bmanagement\s+team\b|\bdoor\s+drop\b|\bdrivers?\b\W+(?:\w+\W+){0,4}not\s+(?:help\w*|giv\w*|return\w*)|\btransport\s+from\b|\bnever\s+return\w*\b|\b(?:thieves|goons)\b",
         r"\b(?:rude|abusive|unprofessional|misbehav\w*|arrogan\w*|disrespect\w*|impolite|irresponsible)\b",
         r"\bdrivers?\b\W+(?:\w+\W+){0,6}(?:late|delay\w*|rude|abusive|speed\w*|rash|wait\w*|behav\w*|attitude|ignor\w*|exceed\w*|refus\w*|careless)\b",
         r"\b(?:late|rude|abusive|unprofessional|irresponsible|careless|ignor\w*|speeding)\s+drivers?\b",
         r"\b(?:cabs?|vehicles?|shuttles?|buses|bus)\b\W+(?:\w+\W+){0,4}(?:late|delay\w*|never|not\s+(?:arriv\w*|come|show\w*|pick\w*|wait\w*|assign\w*|provid\w*|available)|did\s*n'?t\s+(?:come|arrive|show))\b",
         r"\b(?:no|not|insufficient|zero)\s+(?:enough\s+|sufficient\s+)?(?:cabs?|vehicles?)\b",
         r"\bvendors?\b|\btransport(?:ation)?\s+(?:team|service|services|management|desk|vendor|vendors|provider|providers|staff|facility)\b",
         r"\bmgmt\b|\b(?:transport|bad|worst|poor|no\s+proper)\s+(?:management|mgmt)\b|\bmanagement\s+(?:is|was|very|worst)\b|\bstaffs?\b|\bhandlers?\b|\bfmg\b|\bcab\s+services?\s+(?:provided|provider)\b|\bworst\s+cab\s+services?\b",
         r"\bdon'?t\s+wait\b|\bdoesn'?t\s+wait\b|\bdidn'?t\s+wait\b|\bwaiting\s+time\b|\bnot\s+picked\s+up\b",
     ]},
    {"id": "SUPPORT_HELPDESK", "family": "Operations", "nature": "operational",
     "label": "Helpdesk / customer support unreachable, unhelpful or silent",
     "patterns": [
         r"\b(?:waste|worst|useless)\s+support\b|\bhelp\s+team\b|\b(?:no\s+one|nobody|no\s+body)\s+(?:has\s+)?respond\w*|\bcut\s+the\s+call\b|\bline\s+disconnects\b",
         r"\bhelp\s*desk\b|\bhelpdesk\b|\bhelpline\b|\bsahayta\b|\bsaheta\b|\bivr\b",
         r"\bcustomer\s+(?:support|service|care)\b|\b(?:app|bad|no|poor|useless|proper|zero|good|the)\s+support(?:\s+(?:team|system|staff))?\b|\bsupport\s+(?:team|system|staff|desk)\b|\bescalat\w*",
         r"\b(?:no|not)\s+(?:any\s+)?(?:response|reply)\b|\bnobody\s+(?:is\s+)?(?:picking|receiving|answer\w*)",
         r"\b(?:not|n't)\s+(?:receiving|picking|answering|attend\w*)\s+(?:my\s+|the\s+)?calls?\b",
         r"\bno\s+one\s+(?:is\s+)?help\w*|\bnot\s+able\s+to\s+connect\s+with\s+helpdesk\b|\bno\s+feedback\s+link\b|\bunable\s+to\s+reach\s+helpdesk",
     ]},
    # ---------------------------------------------------------------- Engagement, usability and requests
    {"id": "FORCED_RATING", "family": "Engagement & UX", "nature": "usability",
     "label": "Forced / repeated rating or feedback prompt, cannot skip",
     "patterns": [
         r"\bplay\s*store\s+review\w*|\bnot\s+accepting\b\W+(?:\w+\W+){0,6}(?:star|rating)|\buntil\s+i\s+gave\s+\w*\s*(?:5|five)\s*star|\bnotifying\b\W+(?:\w+\W+){0,6}review",
         r"\b(?:force|forcing|forced|forcefully|compel\w*|compulsor\w*|mandatory|mandatorily)\W+(?:\w+\W+){0,6}(?:rat\w*|review|feedback|survey|star)",
         r"\b(?:rat\w*|review|feedback|survey)\W+(?:\w+\W+){0,6}(?:mandatory|compulsor\w*|forced|forcing)\b",
         r"\bskip\W+(?:\w+\W+){0,3}(?:rat\w*|feedback|review)|\b(?:rating|feedback|review)\W+(?:\w+\W+){0,3}skip\b",
         r"\b(?:asks?|asking)\W+(?:\w+\W+){0,4}(?:rat\w*|review|feedback)\b",
         r"\b(?:required|require|have\s+to|has\s+to|need\s+to|must)\W+(?:\w+\W+){0,3}(?:rate|review|give\s+(?:a\s+)?(?:rating|feedback|review))\b",
         r"\bsurvey\b|\brate\s+the\s+trip\s+before\b|\bnot\s+do\s+the\s+star\b",
     ]},
    {"id": "FEEDBACK_FLOW_BROKEN", "family": "Engagement & UX", "nature": "technical",
     "label": "Trip rating/feedback cannot be given or edited; no reply to feedback",
     "patterns": [
         r"\bno\s+feedback\s+(?:option|link|button)\b|\b(?:does|doesn\'?t|don\'?t|not)\s+(?:not\s+)?allow\s+(?:any\s+)?feedback\b",
         r"\b(?:unable|not\s+able|can'?t|cannot|no\s+option|not\s+allow\w*|glitch\w*|bugs?)\W+(?:\w+\W+){0,6}(?:rat(?:e|ing)|feedback)\b",
         r"\b(?:rat(?:e|ing)|feedback)\W+(?:\w+\W+){0,6}(?:not\s+(?:received|working|allowed)|never|glitch\w*|bug\w*|error|lock\w*)",
         r"\bno\s+option\s+for\s+reply\b|\bnever\s+get\s+answer\s+for\s+a\s+bad\s+feedback\b|\btrip\s+ratings?\s+were\s+not\b",
     ]},
    {"id": "UI_UX", "family": "Engagement & UX", "nature": "usability",
     "label": "Interface not user-friendly, confusing or worse after redesign",
     "patterns": [
         r"\bfonts?\b|\bcolou?r\b|\binvisible\b|\bunclear\b",
         r"\buser[\s-]?friendly\b|\bnot\s+(?:very\s+)?(?:easy|simple|intuitive)\b|\b(?:ui|ux)\b|\binterface\b|\bintuitive\b",
         r"\bconfus\w*\b|\bcomplicated\b|\bsimplif\w*|\bmore\s+(?:number\s+of\s+)?taps\b|\bmore\s+steps\b",
         r"\bdesign\b|\blayout\b|\bminimalist\b|\bclutter\w*\b|\bhard\s+to\s+(?:use|find|navigate|search)\b|\bdifficult\s+to\s+(?:use|find|navigate)\b",
         r"\bfull\s+screen\s+banner\b|\btoo\s+many\s+confusion\b|\bvery\s+basic\b",
     ]},
    {"id": "FEATURE_REQUEST", "family": "Engagement & UX", "nature": "usability",
     "label": "Missing feature requested (dark mode, driver chat/call, co-passenger view, etc.)",
     "patterns": [
         r"\bco[\s-]?employees?\b|\bshould\s+retain\b|\bmust\s+be\s+updated\b|\bwould\s+be\s+very\s+useful\b|\bfavou?rites?\b",
         r"\bdark\s*-?mode\b|\bdarkmode\b|\bfull\s+white\b",
         r"\boffline\s+mode\b|\b(?:cab|co)[\s-]?mates?\b|\bfellow\b|\bco[\s-]?passengers?\b|\bwho\s+all\s+are\b|\bpeople\s+who\s+are\s+aligned\b",
         r"\bweek[\s-]?off\b|\bmonthly\s+view\b|\b24[\s-]?(?:hr|hrs|hour)\b|\bam\s*/\s*pm\b|\bdefault\s+floor\b",
         r"\b(?:please|kindly)\s+(?:add|provide|enable)\b|\bshould\s+(?:have|add|provide|include)\s+(?:a|an|the|some)?\s*(?:option|feature|way)\b|\bwould\s+be\s+(?:nice|better|helpful|great)\b|\bsuggestion\b|\bthere\s+should\s+be\b|\badd\s+(?:a|an)\s+(?:option|feature|place|chat)\b|\bshould\s+be\s+available\b",
     ]},
    {"id": "DRIVER_CONTACT", "family": "Engagement & UX", "nature": "usability",
     "label": "Cannot call/chat with driver; call audio problems",
     "patterns": [
         r"\bcontact\s+(?:the\s+)?driver\b|\bchat\s*box\b|\b(?:disable|disabled|removed?)\b\W+(?:\w+\W+){0,3}driver\s+call\b|\bdriver\s+call\s+support\b|\bhide\s+the\s+contact\s+driver\b",
         r"\bno\s+(?:calling|call|chat|messag\w*)\s+(?:option|feature|icon)\b",
         r"\b(?:add|provide|have|need)\s+(?:a\s+|an\s+|the\s+)?(?:chat|messag\w*)\b",
         r"\bunable\s+to\s+(?:contact|call|reach)\s+(?:the\s+)?driver\b|\b(?:option|way)\s+to\s+(?:call|contact|chat|message)\b",
         r"\bcalling\s+(?:issue|feature|option)\b|\bnot\s+audible\b|\b(?:chat|message)\s+(?:icon|feature|option)\b",
         r"\bnot\s+able\s+to\s+(?:call|contact)\b|\bcan'?t\s+(?:call|contact)\b|\bcall\s+(?:option|button)\b|\bcan(?:not)?\s+contact\b",
     ]},
    {"id": "PERMISSIONS_CONSENT", "family": "Engagement & UX", "nature": "policy",
     "label": "Permission / consent prompts, privacy, battery",
     "patterns": [
         r"\bterms\s+and\s+agreements?\b|\btransport\s+polic(?:y|ies)\b\W+(?:\w+\W+){0,6}(?:again|every|always)|\bagree\s+and\s+agree\b",
         r"\bpermission\w*|\bmicrophone\b|\bmic\b|\bread(?:ing)?\s+(?:my\s+)?phone\b|\bsms\s+read\b|\bbattery\b|\bprivacy\b|\bsuspicious\b",
         r"\bi\s+agree\b|\bpolic(?:y|ies)\s+(?:agree\w*|accept\w*)|\b(?:accept|agree)\w*\W+(?:\w+\W+){0,4}(?:polic\w*|terms|t&c|transport\s+polic\w*)\b",
         r"\bterms\s+and\s+conditions\b|\blocation\s+accuracy\b|\bturn\s+on\s+notifications\b|\bpolicy\s+aggreement\b",
     ]},
    # ---------------------------------------------------------------- Cross-cutting tags
    {"id": "SAFETY", "family": "Cross-cutting", "nature": "cross-cutting",
     "label": "Safety / security concern mentioned (women's safety, SOS, speeding, late night)",
     "patterns": [
         r"\bsos\b|\bwomen'?s?\b|\bwoman\b|\bfemale\b|\bladies\b|\bgirls?\b|\bsafety\b|\bunsafe\b|\bemergency\b|\bharass\w*",
         r"\brash\s+driv\w*|\bspeed\w*\s+limit\b|\bexceed\w*\s+(?:the\s+)?speed\b|\bdangerous\b|\blate\s+night\b|\bmidnight\b|\bafraid\b|\bat\s+night\b|\b2:30\s*am\b",
     ]},
    {"id": "UPDATE_REGRESSION", "family": "Cross-cutting", "nature": "cross-cutting",
     "label": "Problem attributed to an app update / redesign",
     "patterns": [
         r"\bprevious\s+(?:application|app)\b|\blatest\s+updates?\b",
         r"\b(?:after|since|following|post)\s+(?:the\s+|an?\s+|this\s+|every\s+|latest\s+|recent\s+)?(?:new\s+|latest\s+|recent\s+|last\s+)?(?:update|upgrade|version|release|enhancement)s?\b",
         r"\b(?:new|latest|recent|last)\s+(?:update|upgrade|version|release|ui|enhancement|features?)s?\b|\bupdate\s+(?:made|has|have|is|was|ruined|broke)\b",
         r"\b(?:old|previous|earlier)\s+(?:app|version|ui|interface)\b|\bbring\s+(?:back\s+)?the\s+old\b|\bused\s+to\s+(?:work|be)\b|\bwhenever\s+i\s+update\b|\bits\s+update\b",
         r"\bbefore\s+the\s+(?:upgrade|update)\b|\bnow\s+(?:not|that)\b|\bfrom\s+yesterday\b|\b2026\s+ui\b",
     ]},
    {"id": "WORKPLACE_FEATURE", "family": "Cross-cutting", "nature": "cross-cutting",
     "label": "Desk / seat / meeting-room (non-commute) feature",
     "patterns": [r"\bdesk\b|\bseat\s+number\b|\bfloor\b|\bmeeting\s+room\b|\bworkspace\b"]},
]

GENERIC_NEGATIVE = (r"\b(?:worst|useless|waste|wasted|pathetic|terrible|terible|bad|poor|bekaar|bekar|bakwas|wrost|wrst|trash|horrible|"
                    r"third\s+class|disaster|garbage|worthless|lazy|disgusting|awful|ghastly|mediocre|hopeless|rubbish|shit\w*|ganda|"
                    r"not\s+(?:good|great|nice|useful|helpful|recommended|reliable|efficient|satisf\w*)|unreliable|disappointing)\b")

# Positive themes, applied only to 4-5 star reviews.
PRAISE = [
    {"id": "EASE_OF_USE", "patterns": [r"\beasy\b|\buser[\s-]?friendly\b|\bsimple\b|\bsmooth\w*\b|\bconvenient\b|\binterface\b|\bintuitive\b|\bseamless\b"]},
    {"id": "TRACKING_ETA", "patterns": [r"\btrack\w*\b|\blive\s+location\b|\breal[\s-]?time\b|\beta\b|\blocation\b"]},
    {"id": "PUNCTUAL_RELIABLE", "patterns": [r"\bon[\s-]?time\b|\bpunctual\w*\b|\btimely\b|\breliable\b"]},
    {"id": "SAFETY_SECURITY", "patterns": [r"\bsafe\w*\b|\bsecur\w*\b"]},
    {"id": "SERVICE_DRIVERS_SUPPORT", "patterns": [r"\bdrivers?\b|\bsupport\b|\bhelpful\b|\bstaff\b|\bservice\b"]},
    {"id": "BOOKING_CONVENIENCE", "patterns": [r"\bbook\w*\b|\bschedul\w*\b|\broster\w*\b"]},
    {"id": "GENERAL_POSITIVE", "patterns": [r"\b(?:good|nice|great|excellent|best|awesome|super|amazing|wonderful|fantastic|perfect|love\w*)\b"]},
]