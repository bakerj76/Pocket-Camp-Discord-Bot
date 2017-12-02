CREATE TABLE `friend_codes` (
    `discord_id` text PRIMARY KEY,
    `discord_name` text NOT NULL,
    `animal_crossing_name` text NOT NULL,
    `friend_code` text NOT NULL
);
