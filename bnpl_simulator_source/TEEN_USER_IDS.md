# Valid User IDs with Age Below 20

## Summary
Found **2,082 users** with age below 20 in the database.

## Sample Valid Teen User IDs (Age < 20)

Here are some valid UUID format user IDs for users under 20 years old:

### Age 18 Users:
1. **590fd4ec-6362-4309-8d2e-5ba503eaf3b2** - Age: 18, Female, Credit Score: 804
2. **7ea84932-2b9f-4269-b4db-e2eaea1114ba** - Age: 18, Male, Credit Score: 757
3. **3098f1f3-bcfb-4e90-85f1-776106252e82** - Age: 18, Female, Credit Score: 652
4. **da91ab9d-61ac-4da2-8f4e-3a164cd56e5d** - Age: 18, Non-Binary, Credit Score: 461
5. **ed5c86c6-affc-4f12-b9aa-4c99bf892be9** - Age: 18, Male, Credit Score: 387

### Age 19 Users:
1. **684cfeda-ee3d-4598-8174-2c3e9fcc80f4** - Age: 19, Female, Credit Score: 405
2. **c4c2294b-764a-4cb3-a854-80753de128b3** - Age: 19, Female, Credit Score: 441
3. **b2d466b3-2147-403c-96ae-7cc3061f93bd** - Age: 19, Male, Credit Score: 481
4. **a0f6a424-088e-4be4-bbaf-4de6473eb164** - Age: 19, Male, Credit Score: 424
5. **b76b0d92-3674-49d2-b736-25e9b899198a** - Age: 19, Male, Credit Score: 535

## Verification
All these user IDs are valid UUID format (36 characters) and exist in the database. You can verify any of them using:

```bash
curl "http://localhost:8000/users/[USER_ID]"
```

## Usage
These user IDs can be used with the BNPL Simulator API for testing scenarios involving teen users, parental controls, or age-based restrictions.

## Note
The user ID `7ea84932-2b9f-4269-b4db-e2eaea1114ba3a6e` mentioned in the original issue is invalid (40 characters), but `7ea84932-2b9f-4269-b4db-e2eaea1114ba` (36 characters) is a valid teen user ID.