import ArticleItem from "./ArticleItem.jsx";

export default function ArticleList({ articles, summaries, onSummaryChange, onAskAI }) {
  return (
    <div className="article-list">
      {articles.map((article) => (
        <ArticleItem
          key={article.id}
          article={article}
          summaryState={summaries[article.id]}
          onSummaryChange={(next) => onSummaryChange(article.id, next)}
          onAskAI={onAskAI}
        />
      ))}
    </div>
  );
}
