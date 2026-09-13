function timeAgo(iso) {
  if (!iso) return "";
  const diffMs = Date.now() - new Date(iso).getTime();
  const hrs = Math.floor(diffMs / (1000 * 60 * 60));
  if (hrs < 1) return "Just now";
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function FeaturedStory({ article, onAskAI }) {
  return (
    <section className="featured">
      {article.image_url && (
        <img className="featured-image" src={article.image_url} alt="" loading="lazy" />
      )}
      <div>
        <div className="featured-source">{article.source}</div>
        <h2 className="featured-title">
          <a href={article.url} target="_blank" rel="noreferrer">
            {article.title}
          </a>
        </h2>
        {article.description && <p className="featured-dek">{article.description}</p>}
        <div className="featured-meta">{timeAgo(article.published_at)}</div>
        <div className="article-actions" style={{ marginTop: 12 }}>
          <button className="link-btn" onClick={() => onAskAI(article)}>
            Discuss with AI Briefing →
          </button>
        </div>
      </div>
    </section>
  );
}
