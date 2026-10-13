# Analysis: Maximum Occupancy Algorithm

## Summary

This document explains the complexity, the behavior in special cases, and the
design choices for the requested booking algorithm.

The function processes a list of booking intervals `[start, end)` and returns
a tuple with:

- The maximum number of bookings at the same time (`max_occupancy`).
- The start of the first peak period (`peak_start`).
- The end of that peak period (`peak_end`).

For an empty list, it safely returns `(0, None, None)`.
Any malformed or invalid booking rejects the whole call by raising an
`InvalidBookingError`.

---

## Complexity Analysis

Let `n` be the number of bookings and `m = 2n` be the total number of events
(one start and one end for each booking). We get the following result:

* **Time: `O(n log n)`**
  - Getting and checking each event takes `O(n)`: time grows in a straight
    line. If there are 1,000 bookings, the code makes 1,000 checks.
  - Sorting the events takes `O(m log m)`: putting the events in time order
    means comparing them. This is the slowest step, but it grows very well.
  - Going through the events takes `O(m) = O(n)`: when the data is sorted, we
    only need to go through it once, from start to end, to add and remove
    bookings from the occupancy count.

* **Memory: `O(m)`**
  - Our algorithm uses `O(m)` memory because it creates a start tuple and an
    end tuple for each booking and stores them in a list. If there are more
    bookings, the list grows in size. However, to calculate the result, the
    code uses only a few separate values: one for the number of active
    bookings, one for the maximum, and two to save when the peak starts and
    ends. These use constant extra memory, `O(1)`, because we always use the
    same fixed number of values, no matter how much data we receive.

---

## Special Cases and Possible Risks

After thinking about situations where the code could work worse, I think:

1. There could be memory problems if the API gets many requests at the same
   time. Although `max_occupancy` is fast on its own, if the platform gets
   many HTTP requests from users checking occupancy at the same time, making
   `2n` tuples for every request could use a lot of the web server's memory.
   The algorithm is currently designed for one call at a time, but it does not
   manage memory or requests happening at the same time. **`Not covered`**

2. If a client sends thousands of exactly identical bookings by mistake (for
   example, the same person booking the same room 50 times by mistake), the
   algorithm does not remove repeated entries. It processes each one
   separately, which increases the maximum occupancy. The code is designed to
   count every entry separately, but in a real system it could report too much
   occupancy if there are duplicate bookings caused by spam. **`Covered`**

3. If the lists are already sorted from the start, the algorithm still sorts
   all the events, whatever the order of the input list. If the database
   already returned bookings sorted by start time, the algorithm would not
   use that advantage. In this case, simplicity and one reliable process were
   chosen instead of optimizing special cases where the input is already
   sorted. **`Not covered`**

4. If instant bookings were requested, the current algorithm would reject
   them with an `InvalidBookingError`. The current contract strictly requires
   `start < end`. If in the future it is decided that a user can make a
   booking with zero duration (for example, to clock in at an exact time),
   the algorithm would reject it. **`Covered`**

---

## Design Choices

The specification did not make some parts clear, so we made our own design
choices. They are shown in this table:

| Design choice | Approach | Why |
|---|---|---|
| **Accepting negative integers** | Allow any integer (`int`) as a time, as long as `start < end`. | This keeps the function pure and reusable. If the business needs to limit times to positive values (such as from 0 to 24), that check should happen outside the function, in the API. This lets the function work with any number. |
| **What to do when peak periods are tied** | Return **only the first period in time** when the maximum occupancy is reached. | This makes the result predictable for the product team. We update the peak only when we find a strictly higher occupancy (`>`). |
| **All-or-nothing error policy** | Check all input in the first pass and stop with a clear error at the **first invalid booking**. | This makes sure that the function does not return a partial or incorrect result, and keeps the result correct when the input has errors. |
| **Treating repeated entries separately** | Treat every identical booking as a separate entry, **without removing repeated entries**. | This follows the idea that every booking record represents a real place being used, so each one adds to the occupancy. |

---

## Statement About AI Use

GitHub Copilot with GPT-6 Luna was used as a coding assistant to help plan
ideas, review test cases, and improve this Markdown document through the
Spec-Driven Development (SDD) method. The author manually checked, understood,
and can explain all logic and design choices.
