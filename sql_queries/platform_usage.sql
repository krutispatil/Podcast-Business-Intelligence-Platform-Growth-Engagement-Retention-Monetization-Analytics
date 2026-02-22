SELECT

platform,
COUNT(*) listens

FROM sessions

GROUP BY platform;
