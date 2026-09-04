import "./VideoPlayer.css";


export default function VideoPlayer({ videoId }) {
  if (!videoId) return null;

  return (
    <div className="video-player-wrap">
      <div className="video-player-aspect">
        <iframe
          src={`https://www.youtube.com/embed/${videoId}`}
          title="YouTube video player"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
        />
      </div>
    </div>
  );
}
