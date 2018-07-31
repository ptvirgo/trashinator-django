module TestUpdateTrashPage exposing (..)

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, int, intRange, list, string)
import Test exposing (..)

import Date

import Models exposing (..)
import UpdateTrashPage exposing (..)


testTrash : Trash
testTrash =
    { date = Date.fromTime 1532750209000
    , amount = Gallons 0
    }

testPage : TrashPage
testPage = { trash = Just testTrash, error = Nothing, token = "fake token" }

testChangeAmount : Test
testChangeAmount = describe "ChangeAmount Meessage"
    [ fuzz (intRange 0 10) "ChangeAmount changes amount of trash" <| \i ->
        let txt = toString i
            x = toFloat i
            newPage =
                { testPage
                | trash = Just { testTrash | amount = Gallons x }
                , error = Just "... remember to save your changes!"
                }
        in Expect.equal
            ( updateTrashPage (ChangeAmount txt) testPage )
            ( newPage, Cmd.none )

    , fuzz (intRange -10 -1) "ChangeAmount rejects numbers < 0" <| \i ->
        let txt = toString i
            newPage = { testPage | error = Just "Amount must be 0 or more" }
        in Expect.equal
            ( updateTrashPage (ChangeAmount txt) testPage )
            ( newPage, Cmd.none)

    , test "ChangeAmount rejects text strings" <| \_ ->
        let newPage = { testPage | error = Just "Amount must be a number" }
        in Expect.equal
            ( updateTrashPage (ChangeAmount "oops") testPage )
            ( newPage, Cmd.none )
    ]

testNewTrash : Test
testNewTrash = describe "NewTrash Message"
    [ fuzz2 (intRange 0 10) string "NewTrash replaces trash" <| \i s ->
        let x = toFloat i
            errPage = { testPage | error = Just s }
            newTrash =
                { testTrash
                | amount = Gallons x
                , date = Date.fromTime 1533006358000
                }
            newPage = { testPage | trash = Just newTrash }
        in Expect.equal
            ( updateTrashPage (NewTrash newTrash) errPage )
            ( newPage, Cmd.none )
    ]

testNewError : Test
testNewError = describe "NewError Message"
    [ fuzz string "NewError replaces empty error message" <| \s ->
        let newPage = { testPage | error = Just s }
        in Expect.equal
            ( updateTrashPage (NewError s) testPage )
            ( newPage, Cmd.none )

    , fuzz2 string string "NewError replaces prior error message" <| \s1 s2 ->
        let oldPage = { testPage | error = Just s1 }
            newPage = { testPage | error = Just s2 }
        in Expect.equal
            ( updateTrashPage (NewError s2) oldPage )
            ( newPage, Cmd.none )
    ]
