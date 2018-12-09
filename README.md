# Multiprocess Me

###
Usage: We are going to create a performance optimized web scraper that uses `Queues` and `Multiprocessing` in Python that will allow a user to define a set of domains, put those domains in a queue, and use multiple processes to scrape HTML for those domains and store the results on disk.

With the usage of `Queues`, users will be able to see constant feedback from the various processes as well.

### Features
1. The user will have the following menu list to choose from:
    ```
    1. Add a domain name
    2. Start processing queue
    3. Stop processing queue
    4. Display logs
    5. Exit
    ```

1. Each domain that is added and processed by a worker must do the following:
      * Send a start processing message to the log queue
      * Retreive the HTML from the domain URL specified and save to disk
      * Send a finished processing message to the log queue

#### Resources
https://docs.python.org/3/library/multiprocessing.html#multiprocessing-examples
