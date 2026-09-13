export function LoadingState() {
  return (
    <div className="state-block">
      <div className="spinner" />
      Fetching the latest coverage…
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state-block">
      <div className="state-title">Couldn't load the news</div>
      <p>{message}</p>
      {onRetry && (
        <button className="link-btn" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ query }) {
  return (
    <div className="state-block">
      <div className="state-title">No stories found</div>
      <p>{query ? `Nothing matched "${query}". Try a different search.` : "Check back shortly."}</p>
    </div>
  );
}
