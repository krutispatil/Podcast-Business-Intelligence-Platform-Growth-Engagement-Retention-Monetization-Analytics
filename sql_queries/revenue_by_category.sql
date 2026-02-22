SELECT
p.category,
SUM(r.revenue_generated) total_revenue

FROM revenue r

JOIN episodes e
ON r.episode_id=e.episode_id

JOIN podcasts p
ON e.podcast_id=p.podcast_id

GROUP BY p.category
ORDER BY total_revenue DESC;
