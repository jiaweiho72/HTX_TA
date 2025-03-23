// components/SearchUI.tsx
import React from "react";
import {
  ErrorBoundary,
  Facet,
  SearchProvider,
  SearchBox,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  Sorting,
  WithSearch,
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

// Connector configuration: Adjust host as needed.
const connector = new ElasticsearchAPIConnector({
  host: "http://localhost:9200",
  index: "cv-transcriptions",
});

// Define sorting options.
const SORT_OPTIONS = [
  {
    name: "Relevance",
    value: [],
  },
  {
    name: "Filename",
    value: [{ field: "filename.keyword", direction: "asc" }],
  },
];

// Define search configuration.
const config = {
  debug: true,
  apiConnector: connector,
  alwaysSearchOnInitialLoad: true,
  searchQuery: {
    // Limit search fields to avoid errors (e.g., duration is not searched since it's a keyword).
    search_fields: {
      generated_text: {},
    },
    result_fields: {
      generated_text: { snippet: { size: 100, fallback: true } },
      duration: { raw: {} },
      age: { raw: {} },
      gender: { raw: {} },
      accent: { raw: {} },
      filename: { raw: {} },
    },
    // Define facets for filtering.
    facets: {
      age: { type: "value", label: "Age" },
      gender: { type: "value", label: "Gender" },
      accent: { type: "value", label: "Accent" },
    },
  },
};

export default function SearchUI() {
  return (
    <SearchProvider config={config}>
      <WithSearch
        mapContextToProps={(context: { wasSearched: boolean }) => ({
          wasSearched: context.wasSearched,
        })}
      >
        {({ wasSearched }: { wasSearched: boolean }) => (
          <div className="container">
            <ErrorBoundary>
              <Layout
                header={<SearchBox debounceLength={300} searchAsYouType={true} />}
                sideContent={
                  <div>
                    {wasSearched && (
                      <Sorting label="Sort by" sortOptions={SORT_OPTIONS} />
                    )}
                    <Facet
                      field="age"
                      label="Age"
                      filterType="any"
                      isFilterable={true}
                    />
                    <Facet
                      field="gender"
                      label="Gender"
                      filterType="any"
                      isFilterable={true}
                    />
                    <Facet
                      field="accent"
                      label="Accent"
                      filterType="any"
                      isFilterable={true}
                    />
                  </div>
                }
                bodyContent={<Results titleField="generated_text" />}
                bodyHeader={
                  <>
                    {wasSearched && <PagingInfo />}
                    {wasSearched && <ResultsPerPage />}
                  </>
                }
                bodyFooter={<Paging />}
              />
            </ErrorBoundary>
          </div>
        )}
      </WithSearch>
    </SearchProvider>
  );
}
