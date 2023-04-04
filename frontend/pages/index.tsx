import { Card, CardContent, CircularProgress } from "@material-ui/core";
import { LocationOnOutlined, TodayOutlined } from "@material-ui/icons";
import Head from "next/head";
import React, { useEffect, useState } from "react";
import FetchError from "../components/FetchError";
import TopAppbar from "../components/TopAppbar";
import { EventDetails } from "../types/event";
import { API_URL, DEFAULT_ERR_MESSAGE } from "../utils/constants";

/** Home Page */
const Index = () => {
  const [fetching, setFetching] = useState(false);
  const [fetchingR, setFetchingR] = useState(false);
  const [fetchErr, setFetchErr] = useState({
    error: false,
    message: "",
  });
  const [events, setEvents] = useState<EventDetails[]>([]);
  const [rEvents, setRevents] = useState<EventDetails[]>([]);

  useEffect(() => {
    setFetching(true);
    // Fetch Events

    fetch(API_URL, {
      mode: "cors",
      method: "GET",
    })
      .then((res) => {
        if (res.ok) {
          return res.json();
        }
        throw new Error();
      })
      .then((res) => setEvents(res["events"]))
      .catch((err) =>
        setFetchErr({ error: true, message: DEFAULT_ERR_MESSAGE })
      )
      .finally(() => setFetching(false));

    // Fetch Recommended events
    setFetchingR(true);
    fetch(`${API_URL}/recommended/12345`, {
      mode: "cors",
      method: "GET",
    })
      .then((res) => {
        if (res.ok) {
          return res.json();
        }
        throw new Error();
      })
      .then((res) => setRevents(res["events"]))
      .catch((err) =>
        setFetchErr({ error: true, message: DEFAULT_ERR_MESSAGE })
      )
      .finally(() => setFetchingR(false));
  }, []);

  const upcomingEvents = [...events].splice(0, 4);
  const popularEvents = [...rEvents].splice(0, 4);

  return (
    <>
      <Head>
        <title>Home</title>
      </Head>
      <TopAppbar />
      {fetching || fetchingR ? (
        <div className="container mt-4 mx-auto">
          <CircularProgress />
        </div>
      ) : fetchErr.error ? (
        <FetchError errorMessage={fetchErr.message} reload />
      ) : (
        <>
          <div className="bg-gray-100">
            <div className="container mx-auto pt-4 pb-6">
              <h6 className="text-lg mb-2">Upcoming Events</h6>
              <div className="grid grid-cols-4 gap-3">
                {upcomingEvents.map((event) => (
                  <Card key={event.url}>
                    <CardContent>
                      <div className="grid gap-2">
                        <p className="font-medium">{event.name}</p>

                        <div className="flex gap-1 items-center text-gray-700">
                          <TodayOutlined />
                          <p className="text-sm">
                            {new Date(event.start_date * 1000).toDateString()}
                          </p>
                        </div>

                        <div className="flex gap-1 items-center text-gray-600">
                          <LocationOnOutlined />
                          <p className="text-sm">{event.location}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          <div className="container mx-auto py-4">
            <h6 className="text-lg mb-2">Recommended Events</h6>
            <div className="grid grid-cols-4 gap-3">
              {rEvents.map((event, idx) => (
                <a
                  href={event.url}
                  key={idx}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  <Card>
                    <img
                      src={event.banner_url}
                      alt=""
                      className="object-cover h-64 w-full "
                    />
                    <CardContent>
                      <div className="grid gap-2">
                        <p className="text-lg font-medium">{event.name}</p>

                        <div className="flex gap-1 items-center text-gray-700">
                          <TodayOutlined />
                          <p className="text-sm">
                            {new Date(event.start_date * 1000).toDateString()}
                          </p>
                        </div>

                        <div className="flex gap-1 items-center text-gray-600">
                          <LocationOnOutlined />
                          <p className="text-sm">{event.location}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </a>
              ))}
            </div>
          </div>

          <div className="container mx-auto py-4">
            <h6 className="text-lg mb-2">Popular Events</h6>
            <div className="grid grid-cols-4 gap-3">
              {popularEvents.map((event, idx) => (
                <a
                  href={event.url}
                  key={idx}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  <Card>
                    <img
                      src={event.banner_url}
                      alt=""
                      className="object-cover h-64 w-full "
                    />
                    <CardContent>
                      <div className="grid gap-2">
                        <p className="text-lg font-medium">{event.name}</p>

                        <div className="flex gap-1 items-center text-gray-700">
                          <TodayOutlined />
                          <p className="text-sm">
                            {new Date(event.start_date * 1000).toDateString()}
                          </p>
                        </div>

                        <div className="flex gap-1 items-center text-gray-600">
                          <LocationOnOutlined />
                          <p className="text-sm">{event.location}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </a>
              ))}
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default Index;
