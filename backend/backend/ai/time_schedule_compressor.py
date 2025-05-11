from backend.shared.event import Event
from sklearn.feature_extraction.text import TfidfVectorizer
import hdbscan
import numpy as np


class TimeScheduleCompressor:
    def __init__(self):
        """Initialize the TimeScheduleCompressor."""
        pass

    def compress(
        self,
        events: list[Event],
        min_cluster_size: int = 4,
        show_n_events_per_cluster: int = 5,
        top_n_features: int = 5,
    ) -> str:
        """
        Compress the list of events into a summarized string representation.

        Args:
            events (List[Event]): The list of events to compress.

        Returns:
            str: The compressed string representation of the events.
        """

        # Combine title and description for each event
        events_text = [(event.title + " " + event.description) for event in events]

        # Create and fit TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(events_text)

        # Perform HDBSCAN clustering
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric="euclidean",
            cluster_selection_method="eom",
        )
        cluster_labels = clusterer.fit_predict(tfidf_matrix)

        # Map events to cluster labels
        event_clusters = {}
        for event, label in zip(events, cluster_labels):
            event_clusters[event] = label

        feature_names = vectorizer.get_feature_names_out()

        # Prepare output string
        output_lines: list[str] = []

        # Get unique labels and sort clusters by number of events, descending
        unique_labels = set(cluster_labels)
        unique_labels = sorted(
            unique_labels, key=lambda x: sum(cluster_labels == x), reverse=True
        )

        # Set the noise cluster (-1) to the last position
        if -1 in unique_labels:
            unique_labels.remove(-1)
            unique_labels.append(-1)

        for i in unique_labels:
            cluster_events = [event for event in events if event_clusters[event] == i]

            n_events = len(cluster_events)

            if i == -1:
                output_lines.append(f"\nUnclustered ({n_events} events):")
            else:
                output_lines.append(f"\nCluster {i} ({n_events} events):")

            if n_events == 0:
                continue  # Skip empty clusters

            # Compute start and end dates for the cluster
            start_dates = [event.start for event in cluster_events]
            end_dates = [event.end for event in cluster_events]

            cluster_start = min(start_dates)
            cluster_end = max(end_dates)

            number_of_days = (cluster_end - cluster_start).days + 1

            # Format dates (ensure datetime objects)
            cluster_start_str = cluster_start.strftime("%Y-%m-%d")
            cluster_end_str = cluster_end.strftime("%Y-%m-%d")

            # Append time information
            output_lines.append(
                f"From {cluster_start_str} to {cluster_end_str} ({number_of_days} days)"
            )

            # Get top features for the cluster
            if i != -1:
                cluster_indices = np.where(cluster_labels == i)[0]
                cluster_tfidf = tfidf_matrix[cluster_indices].toarray().mean(axis=0)  # type: ignore
                top_features_idx = cluster_tfidf.argsort()[-top_n_features:][
                    ::-1
                ]  # Get top_n_features
                top_features = [feature_names[idx] for idx in top_features_idx]
                output_lines.append(f"\nTop terms: {', '.join(top_features)}")  # type: ignore

            # Append event titles
            output_lines.append("Events:")
            n = len(cluster_events) if i == -1 else show_n_events_per_cluster
            for event in cluster_events[:n]:
                output_lines.append(f"- {event.title}")
            if len(cluster_events) > n:
                output_lines.append(f"  ... and {len(cluster_events) - n} more events")

            # Longest description in the cluster
            longest_description_event = max(
                cluster_events, key=lambda x: len(x.description) if x.description else 0
            )
            output_lines.append("\nLongest description:")
            output_lines.append("'" * 3)
            output_lines.append(longest_description_event.description.strip())
            output_lines.append("'" * 3)

        # Join all lines into a single string
        output_str = "\n".join(output_lines)

        return output_str
