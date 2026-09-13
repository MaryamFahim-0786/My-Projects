import { summarizeArticle } from "../api/client";

function timeAgo(iso) {
  if (!iso) return "";
  const diffMs = Date.now() - new Date(iso).getTime();
  const hrs = Math.floor(diffMs / (1000 * 60 * 60));
  if (hrs < 1) return "Just now";
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function ArticleItem({ article, summaryState, onSummaryChange, onAskAI }) {
  const state = summaryState || { status: "idle" };

  async function handleSummarize() {
    if (state.status === "loading" || state.status === "done") {
      onSummaryChange({ ...state, expanded: !state.expanded });
      return;
    }
    onSummaryChange({ status: "loading", expanded: true });
    try {
      const result = await summarizeArticle(
        article.title,
        article.content || article.description || article.title
      );
      onSummaryChange({ status: "done", expanded: true, ...result });
    } catch (err) {
      onSummaryChange({ status: "error", expanded: true, error: err.message });
    }
  }

  return (
    <article className="article-row">
      {article.image_url ? (
        <img className="article-thumb" src={article.image_url} alt="" loading="lazy" />
      ) : (
        <div className="article-thumb" />
      )}
      <div>
        <div className="article-source">{article.source}</div>
        <h3 className="article-title">
          <a href={article.url} target="_blank" rel="noreferrer">
            {article.title}
          </a>
        </h3>
        <div className="article-meta">{timeAgo(article.published_at)}</div>
        <div className="article-actions">
          <button className="link-btn" onClick={handleSummarize}>
            {state.status === "loading"
              ? "Summarizing…"
              : state.expanded
              ? "Hide AI summary"
              : "AI summary"}
          </button>
          <button className="link-btn" onClick={() => onAskAI(article)}>
            Ask AI Briefing
          </button>
        </div>

        {state.expanded && state.status === "done" && (
          <div className="summary-box">
            <span className="summary-label">AI summary</span>
            <p>{state.summary}</p>
            {state.key_points?.length > 0 && (
              <ul>
                {state.key_points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {state.expanded && state.status === "error" && (
          <div className="summary-box">
            <span className="summary-error">Couldn't generate a summary: {state.error}</span>
          </div>
        )}
      </div>
    </article>
  );
}
