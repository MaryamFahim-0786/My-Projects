import { useEffect, useState } from "react";
import Masthead from "./components/Masthead.jsx";
import CategoryNav from "./components/CategoryNav.jsx";
import FeaturedStory from "./components/FeaturedStory.jsx";
import ArticleList from "./components/ArticleList.jsx";
import AIBriefing from "./components/AIBriefing.jsx";
import { LoadingState, ErrorState, EmptyState } from "./components/StateBlocks.jsx";
import { getTopHeadlines, searchNews } from "./api/client";

export default function App() {
  const [category, setCategory] = useState("general");
  const [query, setQuery] = useState(null);
  const [articles, setArticles] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | done | error
  const [errorMessage, setErrorMessage] = useState("");
  const [summaries, setSummaries] = useState({});
  const [contextArticle, setContextArticle] = useState(null);

  async function loadFeed() {
    setStatus("loading");
    setErrorMessage("");
    try {
      const data = query ? await searchNews(query) : await getTopHeadlines(category);
      setArticles(data.articles);
      setSummaries({});
      setStatus("done");
    } catch (err) {
      setErrorMessage(err.message);
      setStatus("error");
    }
  }

  useEffect(() => {
    loadFeed();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, query]);

  function handleCategoryChange(next) {
    setQuery(null);
    setCategory(next);
  }

  function handleSummaryChange(articleId, next) {
    setSummaries((prev) => ({ ...prev, [articleId]: next }));
  }

  const [featured, ...rest] = articles;

  return (
    <div className="app-shell">
      <Masthead onSearch={setQuery} activeQuery={query} onClearSearch={() => setQuery(null)} />

      {!query && (
        <CategoryNav active={category} onChange={handleCategoryChange} disabled={status === "loading"} />
      )}

      <div className="layout">
        <main>
          {status === "loading" && <LoadingState />}
          {status === "error" && <ErrorState message={errorMessage} onRetry={loadFeed} />}
          {status === "done" && articles.length === 0 && <EmptyState query={query} />}

          {status === "done" && articles.length > 0 && (
            <>
              {featured && <FeaturedStory article={featured} onAskAI={setContextArticle} />}
              <ArticleList
                articles={rest}
                summaries={summaries}
                onSummaryChange={handleSummaryChange}
                onAskAI={setContextArticle}
              />
            </>
          )}
        </main>

        <AIBriefing contextArticle={contextArticle} onClearContext={() => setContextArticle(null)} />
      </div>
    </div>
  );
}
